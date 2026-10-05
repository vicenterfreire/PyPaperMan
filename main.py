"""Application entry point for the Wallpaper Carousel desktop app."""

import sys

from PySide6.QtWidgets import QApplication

from app import WallpaperApp


def main() -> None:
    """Create the Qt application and run its event loop."""
    application = QApplication(sys.argv)
    application.setApplicationName("Wallpaper Carousel")
    window = WallpaperApp()
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
