"""PySide6 window, tray integration, and carousel interaction logic."""

import os

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QStyle,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from folder_storage import load_settings, save_settings
from wallpaper import set_random_wallpaper


class WallpaperApp(QMainWindow):
    """Manage the user interface and runtime state of the wallpaper carousel."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Wallpaper Carousel")
        self.setMinimumSize(620, 420)

        try:
            self.folders, self.interval = load_settings()
        except (OSError, ValueError) as error:
            self.folders = []
            self.interval = 300
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Could not load the saved settings:\n{error}",
            )

        self.active_folder: str | None = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.change_wallpaper)

        self._build_ui()
        self._build_tray_icon()
        self._apply_style()

    def _build_ui(self) -> None:
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Wallpaper Carousel")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Choose folders and let your desktop rotate automatically.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        self.folder_list = QListWidget()
        self.folder_list.addItems(self.folders)
        self.folder_list.setAlternatingRowColors(True)
        layout.addWidget(self.folder_list, stretch=1)

        folder_buttons = QHBoxLayout()
        add_button = QPushButton("Add folder")
        add_button.clicked.connect(self.add_folder)
        remove_button = QPushButton("Remove selected")
        remove_button.clicked.connect(self.remove_folder)
        active_button = QPushButton("Set active")
        active_button.clicked.connect(self.set_active)
        folder_buttons.addWidget(add_button)
        folder_buttons.addWidget(remove_button)
        folder_buttons.addWidget(active_button)
        layout.addLayout(folder_buttons)

        interval_row = QHBoxLayout()
        interval_label = QLabel("Change interval")
        self.interval_input = QLineEdit(str(self.interval))
        self.interval_input.setPlaceholderText("Seconds")
        self.interval_input.setMaximumWidth(150)
        self.interval_input.editingFinished.connect(self.save_interval)
        interval_row.addWidget(interval_label)
        interval_row.addWidget(self.interval_input)
        interval_row.addStretch()
        interval_row.addWidget(QLabel("seconds"))
        layout.addLayout(interval_row)

        control_row = QHBoxLayout()
        self.status_label = QLabel("Stopped")
        self.status_label.setObjectName("status")
        start_button = QPushButton("Start carousel")
        start_button.setObjectName("primaryButton")
        start_button.clicked.connect(self.start_carousel)
        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.stop_carousel)
        control_row.addWidget(self.status_label)
        control_row.addStretch()
        control_row.addWidget(start_button)
        control_row.addWidget(stop_button)
        layout.addLayout(control_row)

        self.setCentralWidget(central_widget)

    def _build_tray_icon(self) -> None:
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DesktopIcon)
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("Wallpaper Carousel")

        tray_menu = QMenu()
        show_action = QAction("Open Wallpaper Carousel", self)
        show_action.triggered.connect(self.show_window)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._handle_tray_activation)
        self.tray_icon.show()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #171923; color: #edf0f7; }
            QLabel#title { font-size: 24px; font-weight: 700; }
            QLabel#subtitle { color: #a0a7b8; }
            QLabel#status { color: #a0a7b8; }
            QListWidget, QLineEdit {
                background: #222633; border: 1px solid #363d4e;
                border-radius: 8px; padding: 9px;
            }
            QListWidget::item { padding: 7px; }
            QListWidget::item:selected { background: #4f6bed; border-radius: 5px; }
            QPushButton {
                background: #2a3040; border: 1px solid #3a4255;
                border-radius: 8px; padding: 9px 14px;
            }
            QPushButton:hover { background: #363e51; }
            QPushButton#primaryButton {
                background: #4f6bed; border-color: #4f6bed; font-weight: 600;
            }
            QPushButton#primaryButton:hover { background: #6780f3; }
            """
        )

    def add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose wallpaper folder")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.folder_list.addItem(folder)
            self._save_settings()

    def remove_folder(self) -> None:
        index = self.folder_list.currentRow()
        if index >= 0:
            folder = self.folders.pop(index)
            self.folder_list.takeItem(index)
            if self.active_folder == folder:
                self.active_folder = None
            self._save_settings()

    def set_active(self) -> None:
        index = self.folder_list.currentRow()
        if index >= 0:
            self.active_folder = self.folders[index]
            self.status_label.setText(f"Active folder: {self.active_folder}")

    def save_interval(self) -> bool:
        try:
            interval = int(self.interval_input.text())
            if interval < 1:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid interval",
                "Enter a whole number of seconds greater than zero.",
            )
            self.interval_input.setText(str(self.interval))
            return False

        self.interval = interval
        self._save_settings()
        if self.timer.isActive():
            self.timer.setInterval(self.interval * 1000)
        return True

    def _save_settings(self) -> None:
        try:
            save_settings(self.folders, self.interval)
        except OSError as error:
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Could not save the settings:\n{error}",
            )

    def start_carousel(self) -> None:
        if not self.save_interval():
            return
        if not self.active_folder:
            QMessageBox.warning(self, "No active folder", "Select an active folder first.")
            return
        if not os.path.isdir(self.active_folder):
            QMessageBox.warning(
                self, "Folder unavailable", "The active folder cannot be found."
            )
            return

        self.change_wallpaper()
        self.timer.start(self.interval * 1000)
        self.status_label.setText("Carousel running")

    def stop_carousel(self) -> None:
        self.timer.stop()
        self.status_label.setText("Stopped")

    def change_wallpaper(self) -> None:
        if self.active_folder is not None and os.path.isdir(self.active_folder):
            set_random_wallpaper(self.active_folder)

    def show_window(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _handle_tray_activation(
        self, reason: QSystemTrayIcon.ActivationReason
    ) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_window()

    def closeEvent(self, event: QCloseEvent) -> None:
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
            event.ignore()
            self.tray_icon.showMessage(
                "Wallpaper Carousel",
                "The app is still running in the system tray.",
            )
            return

        self.timer.stop()
        self.tray_icon.hide()
        event.accept()
