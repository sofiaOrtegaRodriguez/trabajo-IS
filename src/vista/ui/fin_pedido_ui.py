import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal


class FinPedidoUI(QWidget):

    volver_cesta = pyqtSignal() #Señal que se emite cuando el usuario hace clic en el botón para volver a la cesta
    salir_login = pyqtSignal() #Señal que se emite cuando el usuario hace clic en el botón para salir al login

    def __init__(self, codigo, total, puntos):
        super().__init__()

        self.codigo = codigo # Código del pedido
        self.total = total # Total del pedido
        self.puntos = puntos # Puntos obtenidos

        ui_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ui_pyqt",
            "FinPedidoUI.ui"
        )

        uic.loadUi(ui_path, self)

        self._render()
        self._connect()

    def _connect(self):
        """Conecta los botones de la interfaz a las señales correspondientes."""
        self.btnVolver.clicked.connect(self.volver_cesta.emit)
        self.btnSalir.clicked.connect(self.salir_login.emit)

    def _render(self):
        """Actualiza los elementos de la interfaz con los datos del pedido."""
        self.lblCodigo.setText(f"Pedido #{self.codigo}")
        self.lblTotal.setText(f"{self.total:.2f} €")
        self.lblPuntos.setText(f"+{self.puntos} puntos")