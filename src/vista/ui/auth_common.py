import os

from PyQt5.QtCore import Qt

C_BACKGROUND = "#147DB2"
C_CARD = "#072D44"
C_CREAM = "#FEF5ED"
C_ORANGE = "#FC814A"
C_ORANGE_DARK = "#E66E3A"
C_TEXT_MUTED = "#B6D5E2"
C_TEXT_DIM = "#7B97A5"

_HERE = os.path.dirname(os.path.abspath(__file__))
_IMAGES = os.path.normpath(os.path.join(_HERE, "..", "imagenes"))


def asset(*parts):
    path = os.path.join(_IMAGES, *parts)
    return path if os.path.exists(path) else None
