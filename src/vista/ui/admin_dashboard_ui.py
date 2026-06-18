from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget
import os



class AdminDashboardUI(QWidget):

    productos_clicked = pyqtSignal()
    personal_clicked = pyqtSignal()
    cerrar_sesion = pyqtSignal()

    def __init__(self, sesion, parent=None):
        super().__init__(parent)
        self._sesion = sesion

        # cargar UI
        ui_path = os.path.join(
            os.path.dirname(__file__),
            "../ui_pyqt/admin_dashboard.ui"
        )
        uic.loadUi(ui_path, self)

        #personalizar dinámico
        self._setup_dynamic()

        #señales
        self._connect_signals()

    def _setup_dynamic(self):
        self.greeting_label.setText(f"HOLA {self._sesion.nombre}")

    def _connect_signals(self):
        self.logout_button.clicked.connect(
            lambda: self.cerrar_sesion.emit()
        )

        self.products_button.clicked.connect(
            lambda: self.productos_clicked.emit()
        )

        self.staff_button.clicked.connect(
            lambda: self.personal_clicked.emit()
        )