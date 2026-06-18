import os
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog


class ConfirmarCanjeUI(QDialog):
    """Pop-up modal que pide confirmación antes de canjear los puntos en la cesta."""

    def __init__(self, puntos=0, descuento=0.0, parent=None):
        super().__init__(parent)

        ui_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ui_pyqt",
            "ConfirmarCanjeUI.ui"
        )
        uic.loadUi(ui_path, self)

        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        if puntos and descuento:
            self.lblMensaje.setText(
                f"Vas a canjear {puntos} puntos por un descuento de {descuento:.2f} €.\n"
                "¿Quieres continuar?"
            )

        self.btnCancelar.clicked.connect(self.reject)
        self.btnConfirmar.clicked.connect(self.accept)
