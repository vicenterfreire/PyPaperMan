"""Windows desktop wallpaper selection and update."""

import ctypes
import os
import random


SPI_SETDESKWALLPAPER = 20
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


def set_random_wallpaper(folder: str) -> None:
    """Choose an image from a folder and request that Windows set it as wallpaper."""
    images = [
        os.path.join(folder, filename)
        for filename in os.listdir(folder)
        if filename.lower().endswith(IMAGE_EXTENSIONS)
    ]

    if images:
        image = random.choice(images)
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, image, 3
        )
