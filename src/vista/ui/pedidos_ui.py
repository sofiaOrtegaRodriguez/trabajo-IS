import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QDialog,
    QComboBox, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QBrush

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from src.controlador.ControladorPedidos import ControladorPedidos

controlador = ControladorPedidos()


# ── Paleta de colores ────────────────────────────────────────────────────────
BG        = "#0071AA"
PANEL     = "#052B41"
CARD      = "#052B41"
BORDER    = "#FC814A"
TEXT      = "#FEF5ED"
SUBTEXT   = "#FEF5ED"

STATUS_COLORS = {
    "pagado":     {"bg": "#1C3B2F", "accent": "#34D399", "text": "#34D399"},
    "pendiente":  {"bg": "#3A2A1A", "accent": "#F59E0B", "text": "#F59E0B"},
    "preparando": {"bg": "#1A2B3A", "accent": "#60A5FA", "text": "#60A5FA"},
    "listo":      {"bg": "#2A1A3A", "accent": "#A78BFA", "text": "#A78BFA"},
}

ESTADOS = ["pendiente", "pagado", "preparando", "listo"]

# ── Carga de pedidos desde la base de datos ───────────────────────────────────


def cargar_pedidos_bd():
    """Obtiene todos los pedidos desde la BD y los convierte al formato de la UI."""
    registros = controlador.buscarPedidos() 
    pedidos = []
    for vo in registros:
        # Convertimos la lista de objetos PedidoDetalleVo a un string: "2x Pizza, 1x Coca-Cola"
        nombres_productos = ", ".join([f"{item.cantidad}x {item.nombre_producto}" for item in vo.productos])
        
        pedidos.append({
            "id":        f"#{vo.id}",
            "hora":      vo.hora,
            "usuario":   str(vo.usuario),
            "productos": nombres_productos if nombres_productos else "Sin productos",
            "estado":    vo.estado.lower(),
            "precio":    vo.total,
        })
    return pedidos


# ── Botón de estado (filtro superior) ────────────────────────────────────────
class EstadoBtn(QPushButton):
    def __init__(self, estado, parent=None):
        super().__init__(parent)
        self.estado = estado
        self.activo = False
        self.setText(estado.upper())
        self.setFixedHeight(44)
        self.setCheckable(True)
        c = STATUS_COLORS[estado]
        self._accent = c["accent"]
        self._apply_style(False)
        self.setFont(QFont("Consolas", 10, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)

    def _apply_style(self, activo):
        c = STATUS_COLORS[self.estado]
        if activo:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {c['bg']};
                    color: {c['accent']};
                    border: 2px solid {c['accent']};
                    border-radius: 8px;
                    padding: 0 18px;
                    letter-spacing: 2px;
                }}
                QPushButton:hover {{
                    background: {c['bg']};
                    border-color: {c['accent']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {CARD};
                    color: {SUBTEXT};
                    border: 1.5px solid {BORDER};
                    border-radius: 8px;
                    padding: 0 18px;
                    letter-spacing: 2px;
                }}
                QPushButton:hover {{
                    color: {c['accent']};
                    border-color: {c['accent']};
                    background: {c['bg']};
                }}
            """)

    def set_activo(self, val):
        self.activo = val
        self._apply_style(val)


# ── Fila de pedido ────────────────────────────────────────────────────────────
class FilaPedido(QFrame):
    estado_cambiado = pyqtSignal(str, str)  # id_pedido, nuevo_estado

    def __init__(self, pedido: dict, parent=None):
        super().__init__(parent)
        self.pedido = pedido
        self._build()

    def _build(self):
        c = STATUS_COLORS[self.pedido["estado"]]
        self.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-left: 4px solid {c['accent']};
                border-radius: 10px;
            }}
        """)
        self.setFixedHeight(58)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 10, 0)
        lay.setSpacing(0)

        def cell(text, width, bold=False, color=TEXT):
            lbl = QLabel(text)
            lbl.setFixedWidth(width)
            lbl.setFont(QFont("Consolas", 10, QFont.Bold if bold else QFont.Normal))
            lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")
            lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            return lbl

        lay.addWidget(cell(self.pedido["hora"],     90,  color=SUBTEXT))
        lay.addWidget(cell(self.pedido["id"],        80,  bold=True, color=c['accent']))
        lay.addWidget(cell(self.pedido["usuario"],  140,  color=TEXT))
        lay.addStretch(1)

        prod = QLabel(self.pedido["productos"])
        prod.setFont(QFont("Consolas", 9))
        prod.setStyleSheet(f"color: {SUBTEXT}; background: transparent; border: none;")
        prod.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        prod.setWordWrap(False)
        lay.addWidget(prod, stretch=3)

        lay.addSpacing(12)

        # Badge estado
        badge = QLabel(self.pedido["estado"].upper())
        badge.setFixedSize(90, 26)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFont(QFont("Consolas", 8, QFont.Bold))
        badge.setStyleSheet(f"""
            color: {c['accent']};
            background: {c['bg']};
            border: 1px solid {c['accent']};
            border-radius: 5px;
            padding: 0 6px;
        """)
        lay.addWidget(badge)
        lay.addSpacing(10)

        # Botón MOD
        btn = QPushButton("MOD")
        btn.setFixedSize(58, 32)
        btn.setFont(QFont("Consolas", 9, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT};
                border: 1.5px solid {BORDER};
                border-radius: 6px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: {c['bg']};
                border-color: {c['accent']};
                color: {c['accent']};
            }}
            QPushButton:pressed {{
                background: {c['accent']}33;
            }}
        """)
        btn.clicked.connect(self._modificar)
        lay.addWidget(btn)

    def _modificar(self):
        dlg = ModificarEstadoDialog(self.pedido, self)
        if dlg.exec_() == QDialog.Accepted:
            nuevo = dlg.nuevo_estado
            self.pedido["estado"] = nuevo
            self.estado_cambiado.emit(self.pedido["id"], nuevo)
            self._rebuild()

    def _rebuild(self):
        # Limpiar layout y reconstruir
        old = self.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self._build()


# ── Diálogo para cambiar estado ───────────────────────────────────────────────
class ModificarEstadoDialog(QDialog):
    def __init__(self, pedido, parent=None):
        super().__init__(parent)
        self.nuevo_estado = pedido["estado"]
        self.setWindowTitle("Modificar Estado")
        self.setFixedSize(340, 220)
        self.setStyleSheet(f"""
            QDialog {{
                background: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QLabel {{ color: {TEXT}; background: transparent; }}
            QComboBox {{
                background: {CARD};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                font-family: Consolas;
                font-size: 12px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: {CARD};
                color: {TEXT};
                border: 1px solid {BORDER};
                selection-background-color: {BORDER};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        title = QLabel(f"Pedido {pedido['id']}  ·  {pedido['usuario']}")
        title.setFont(QFont("Consolas", 11, QFont.Bold))
        lay.addWidget(title)

        sub = QLabel("Selecciona el nuevo estado:")
        sub.setFont(QFont("Consolas", 9))
        sub.setStyleSheet(f"color: {SUBTEXT};")
        lay.addWidget(sub)

        self.combo = QComboBox()
        for e in ESTADOS:
            self.combo.addItem(e.upper(), e)
        self.combo.setCurrentIndex(ESTADOS.index(pedido["estado"]))
        lay.addWidget(self.combo)

        lay.addSpacing(4)

        btn_lay = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFont(QFont("Consolas", 9))
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {SUBTEXT};
                border: 1px solid {BORDER}; border-radius: 6px;
            }}
            QPushButton:hover {{ color: {TEXT}; border-color: {TEXT}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Guardar")
        btn_ok.setFixedHeight(36)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setFont(QFont("Consolas", 9, QFont.Bold))
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: #34D39922; color: #34D399;
                border: 1px solid #34D399; border-radius: 6px;
            }}
            QPushButton:hover {{ background: #34D39944; }}
        """)
        btn_ok.clicked.connect(self._guardar)

        btn_lay.addWidget(btn_cancel)
        btn_lay.addWidget(btn_ok)
        lay.addLayout(btn_lay)

    def _guardar(self):
        self.nuevo_estado = self.combo.currentData()
        self.accept()


# ── Ventana principal ─────────────────────────────────────────────────────────
class PedidosApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Pedidos — Tiempo Real")
        self.resize(1000, 680)
        self.pedidos = cargar_pedidos_bd()
        self.filtro_activo = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background: {BG}; }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: {PANEL}; width: 6px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER}; border-radius: 3px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # ── Cabecera ──────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title_lbl = QLabel("PEDIDOS")
        title_lbl.setFont(QFont("Consolas", 22, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {TEXT}; letter-spacing: 4px;")

        self.live_dot = QLabel("● EN VIVO")
        self.live_dot.setFont(QFont("Consolas", 9, QFont.Bold))
        self.live_dot.setStyleSheet("color: #34D399; letter-spacing: 2px;")

        self.clock_lbl = QLabel()
        self.clock_lbl.setFont(QFont("Consolas", 11))
        self.clock_lbl.setStyleSheet(f"color: {SUBTEXT};")
        self._update_clock()

        hdr.addWidget(title_lbl)
        hdr.addSpacing(14)
        hdr.addWidget(self.live_dot)
        hdr.addStretch()
        hdr.addWidget(self.clock_lbl)
        root.addLayout(hdr)

        # Timer reloj
        clk = QTimer(self)
        clk.timeout.connect(self._update_clock)
        clk.start(1000)

        # ── Filtros de estado ─────────────────────────────────────────────────
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet(f"""
            QFrame {{
                background: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        filtros_lay = QHBoxLayout(filtros_frame)
        filtros_lay.setContentsMargins(16, 12, 16, 12)
        filtros_lay.setSpacing(12)

        self.estado_btns = {}
        for estado in ESTADOS:
            btn = EstadoBtn(estado)
            btn.clicked.connect(lambda checked, e=estado: self._toggle_filtro(e))
            self.estado_btns[estado] = btn
            filtros_lay.addWidget(btn)

        root.addWidget(filtros_frame)

        # ── Cabecera de columnas ──────────────────────────────────────────────
        col_frame = QFrame()
        col_frame.setStyleSheet("background: transparent;")
        col_lay = QHBoxLayout(col_frame)
        col_lay.setContentsMargins(18, 0, 10, 0)
        col_lay.setSpacing(0)

        def col_hdr(text, width, stretch=0):
            l = QLabel(text)
            l.setFont(QFont("Consolas", 8, QFont.Bold))
            l.setStyleSheet(f"color: {SUBTEXT}; letter-spacing: 2px;")
            l.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            if width:
                l.setFixedWidth(width)
            return l

        col_lay.addWidget(col_hdr("HORA", 90))
        col_lay.addWidget(col_hdr("ID", 80))
        col_lay.addWidget(col_hdr("USUARIO", 140))
        col_lay.addStretch(1)
        col_lay.addWidget(col_hdr("PRODUCTOS", None), 3)
        col_lay.addSpacing(12)
        col_lay.addWidget(col_hdr("ESTADO", 90))
        col_lay.addSpacing(10)
        col_lay.addWidget(col_hdr("", 58))
        root.addWidget(col_frame)

        # ── Lista de pedidos ──────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.lista_widget = QWidget()
        self.lista_widget.setStyleSheet("background: transparent;")
        self.lista_lay = QVBoxLayout(self.lista_widget)
        self.lista_lay.setContentsMargins(0, 0, 0, 0)
        self.lista_lay.setSpacing(8)
        self.lista_lay.addStretch()

        scroll.setWidget(self.lista_widget)
        root.addWidget(scroll, stretch=1)

        # ── Footer ────────────────────────────────────────────────────────────
        self.footer_lbl = QLabel()
        self.footer_lbl.setFont(QFont("Consolas", 8))
        self.footer_lbl.setStyleSheet(f"color: {SUBTEXT};")
        root.addWidget(self.footer_lbl)

        self._render_pedidos()

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _update_clock(self):
        self.clock_lbl.setText(datetime.now().strftime("%H:%M:%S  ·  %d/%m/%Y"))

    def _toggle_filtro(self, estado):
        if self.filtro_activo == estado:
            self.filtro_activo = None
            self.estado_btns[estado].set_activo(False)
        else:
            if self.filtro_activo:
                self.estado_btns[self.filtro_activo].set_activo(False)
            self.filtro_activo = estado
            self.estado_btns[estado].set_activo(True)
        self._render_pedidos()

    def _render_pedidos(self):
        # Limpiar
        while self.lista_lay.count() > 1:
            item = self.lista_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtrados = [p for p in self.pedidos
                     if self.filtro_activo is None or p["estado"] == self.filtro_activo]

        # Ordenar: más reciente primero
        filtrados.sort(key=lambda p: p["hora"], reverse=True)

        for pedido in filtrados:
            fila = FilaPedido(pedido)
            fila.estado_cambiado.connect(self._on_estado_cambiado)
            self.lista_lay.insertWidget(self.lista_lay.count() - 1, fila)

        total = len(self.pedidos)
        mostrados = len(filtrados)
        filtro_txt = f"· filtro: {self.filtro_activo.upper()}" if self.filtro_activo else "· todos los estados"
        self.footer_lbl.setText(
            f"Mostrando {mostrados} de {total} pedidos  {filtro_txt}"
        )

    def _on_estado_cambiado(self, id_pedido, nuevo_estado):
        # Actualizar en la BD
        id_num = int(id_pedido.replace("#", ""))
        cambio = controlador.actualizarEstado(id_num, nuevo_estado.upper())
        if cambio: #comprueba si se hizo la modificación en la BD, si no, muestra un error
            # Actualizar en memoria y refrescar vista
            for p in self.pedidos:
                if p["id"] == id_pedido:
                    p["estado"] = nuevo_estado
                    break
            self._render_pedidos()

    def _recargar_pedidos(self):
        """Recarga los pedidos desde la BD y refresca la vista."""
        self.pedidos = cargar_pedidos_bd()
        self._render_pedidos()

        # Parpadeo "EN VIVO"
        orig = self.live_dot.styleSheet()
        self.live_dot.setStyleSheet("color: #F59E0B; letter-spacing: 2px;")
        QTimer.singleShot(600, lambda: self.live_dot.setStyleSheet(orig))


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(BG))
    pal.setColor(QPalette.WindowText, QColor(TEXT))
    pal.setColor(QPalette.Base, QColor(CARD))
    pal.setColor(QPalette.AlternateBase, QColor(PANEL))
    pal.setColor(QPalette.Text, QColor(TEXT))
    pal.setColor(QPalette.Button, QColor(PANEL))
    pal.setColor(QPalette.ButtonText, QColor(TEXT))
    app.setPalette(pal)

    win = PedidosApp()
    win.show()
    sys.exit(app.exec_())