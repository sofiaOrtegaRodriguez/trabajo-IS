import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal


class FinPedidoUI(QWidget):

    # 🔥 AQUÍ ESTÁ LA CLAVE: señales reales
    volver_cesta = pyqtSignal()
    salir_login = pyqtSignal()

    def __init__(self, codigo, total, puntos):
        super().__init__()

        self.codigo = codigo
        self.total = total
        self.puntos = puntos

        ui_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ui_pyqt",
            "FinPedidoUI.ui"
        )

        # ✔️ carga correcta
        uic.loadUi(ui_path, self)

        self._render()
        self._connect()

    def _connect(self):
        self.btnVolver.clicked.connect(self.volver_cesta.emit)
        self.btnSalir.clicked.connect(self.salir_login.emit)

    def _render(self):
        self.lblCodigo.setText(f"Pedido #{self.codigo}")
        self.lblTotal.setText(f"{self.total:.2f} €")
        self.lblPuntos.setText(f"+{self.puntos} puntos")