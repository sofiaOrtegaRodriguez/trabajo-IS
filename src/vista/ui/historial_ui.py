"""
Vista del Historial de Pedidos - PyQt5.
"""

import os

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QVBoxLayout

C_BG = "#147DB2"
C_CARD = "#5CA9D0"
C_ORANGE = "#FC814A"
C_WHITE = "#FFFFFF"
C_MUTED = "#B6D5E2"
C_RED_BG = "#4A2020"
C_RED_ACC = "#C06060"


class PedidoCard(QFrame):
    def __init__(self, pedido, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", "PedidoCardUI.ui")
        uic.loadUi(ui_path, self)
        self._render(pedido)

    def _render(self, pedido):
        cancelado = pedido.estado == "cancelado"
        bg = C_RED_BG if cancelado else C_CARD
        accent = C_RED_ACC if cancelado else C_ORANGE
        estado_bg = C_RED_ACC if cancelado else C_BG
        estado_txt = "X  Cancelado" if cancelado else "✓  Completado"

        self.setStyleSheet(f"QFrame#PedidoCardUI{{background:{bg};border-radius:18px;}}QLabel{{background:transparent;}}")

        bar_estado = self.findChild(QFrame, "barEstado")
        if bar_estado is not None:
            bar_estado.setStyleSheet(f"background:{accent};border-radius:3px;")

        self.lblId.setText(f"Pedido #{pedido.id:04d}")
        self.lblBadgeEstado.setText(estado_txt)
        self.lblBadgeEstado.setStyleSheet(
            f"background:{estado_bg};color:{C_WHITE};font-size:11px;font-weight:700;border-radius:10px;padding:4px 12px;"
        )
        self.lblHora.setText(f"{pedido.fecha}     {pedido.hora}")
        self.lblTotal.setText(f"{pedido.total:.2f} €")

        detalle = []
        for prod in pedido.productos:
            detalle.append(f"· {prod.nombre_producto} x{prod.cantidad}   {prod.subtotal:.2f} €")
        self.lblProductos.setText("\n".join(detalle) if detalle else "Sin productos registrados.")


class HistorialUI(QWidget):
    volver_menu = pyqtSignal()
    cerrar_sesion = pyqtSignal()

    def __init__(self, cliente, pedidos, parent=None):
        super().__init__(parent)
        self._cliente = cliente
        self._pedidos = pedidos

        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", "HistorialUI.ui")
        uic.loadUi(ui_path, self)

        self.itemsLayout = self.findChild(QVBoxLayout, "itemsLayout")
        self._connect_signals()
        self._render()

    def _connect_signals(self):
        self.btnBack.clicked.connect(self.volver_menu)
        self.btnLogout.clicked.connect(self._confirmar_cierre)

    def _render(self):
        self._render_header()
        self._render_items()

    def _render_header(self):
        self.lblPuntos.setText(str(self._cliente.puntos))
        self.lblBienvenida.setText(f"Bienvenid@, {self._cliente.nombre}")
        n = len(self._pedidos)
        self.lblNumPedidos.setText(f"{n} pedido{'s' if n != 1 else ''} registrado{'s' if n != 1 else ''}")

    def _render_items(self):
        self._clear_layout(self.itemsLayout)
        if not self._pedidos:
            lbl_empty = QLabel("Aún no tienes pedidos registrados.")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet(f"color:{C_MUTED};font-size:15px;font-weight:600;")
            self.itemsLayout.addWidget(lbl_empty)
            return

        for pedido in self._pedidos:
            self.itemsLayout.addWidget(PedidoCard(pedido))

    def _clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _confirmar_cierre(self):
        self.cerrar_sesion.emit()
