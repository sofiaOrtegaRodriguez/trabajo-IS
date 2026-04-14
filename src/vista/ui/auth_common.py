import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget


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


class IconInput(QFrame):
    def __init__(self, placeholder, icon, password=False, parent=None):
        super().__init__(parent)
        self.setObjectName("iconInput")
        self.setFixedHeight(48)
        self.setStyleSheet(
            f"""
            QFrame#iconInput {{
                background-color: {C_CREAM};
                border-radius: 24px;
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setFixedWidth(18)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent; color: #163246; font-size: 14px;")

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        if password:
            self.input.setEchoMode(QLineEdit.Password)
        self.input.setStyleSheet(
            """
            QLineEdit {
                background: transparent;
                border: none;
                color: #163246;
                font-size: 14px;
            }
            QLineEdit::placeholder {
                color: #8AA1AD;
            }
            """
        )

        layout.addWidget(icon_label)
        layout.addWidget(self.input, 1)

    def text(self):
        return self.input.text()

    def clear(self):
        self.input.clear()

    @property
    def returnPressed(self):
        return self.input.returnPressed


class BrandPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sushi_px = None
        self.brush_px = None
        self._load_assets()
        self._build()

    def _load_assets(self):
        sushi_path = asset("fondos", "sushi_plate.png")
        brush_path = asset("fondos", "brush_stroke.png")
        if sushi_path:
            self.sushi_px = QPixmap(sushi_path)
        if brush_path:
            self.brush_px = QPixmap(brush_path)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(10)

        title = QLabel("sushUle")
        title.setStyleSheet("color: #0B273A; font-size: 26px; font-weight: 800;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        caption = QLabel("El mejor sushi de la Ule")
        caption.setAlignment(Qt.AlignCenter)
        caption.setStyleSheet("color: #23465C; font-size: 14px;")
        layout.addWidget(caption)

        self.hero = QLabel()
        self.hero.setMinimumHeight(210)
        self.hero.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hero, 1)

        footer = QLabel("Ya sabes, si es bueno es SushUle ;)")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #23465C; font-size: 13px;")
        layout.addWidget(footer)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render_hero()

    def _render_hero(self):
        width = max(220, self.hero.width())
        height = max(200, self.hero.height())
        canvas = QPixmap(width, height)
        canvas.fill(Qt.transparent)

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if self.brush_px and not self.brush_px.isNull():
            brush = self.brush_px.scaled(
                int(width * 0.95),
                int(height * 0.55),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation,
            )
            painter.drawPixmap((width - brush.width()) // 2, int(height * 0.18), brush)

        if self.sushi_px and not self.sushi_px.isNull():
            sushi = self.sushi_px.scaled(
                int(width * 0.72),
                int(height * 0.72),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            painter.drawPixmap((width - sushi.width()) // 2, (height - sushi.height()) // 2, sushi)

        painter.setPen(QPen(QColor("#0B273A"), 2))
        for cx, cy, size in ((28, 28, 8), (width - 34, 52, 7), (width - 46, height - 36, 10)):
            painter.drawLine(cx - size, cy, cx + size, cy)
            painter.drawLine(cx, cy - size, cx, cy + size)
        painter.end()

        self.hero.setPixmap(canvas)
