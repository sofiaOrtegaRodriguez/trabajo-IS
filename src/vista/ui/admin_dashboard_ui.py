from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget
import os

"""
    Esta clase representa el panel de administración en la interfaz gráfica.
    Hereda de QWidget y utiliza un archivo .ui (del Designer de Qt) para definir
    su diseño. 
    Proporciona SEÑALES para indicar cuando se ha solicitado cambiar a otras vistas
    (por ejemplo, la vista de PRODUCTOS o la vista de PERSONAL). 
    Además, incluye métodos para personalizar dinámicamente el saludo del administrador 
    y conectar señales a los botones.

    NO se realiza la gestión de productos ni personal en esta clase, eso es responsabilidad del controlador correspondiente.

            Vista
            ↓
            emit
            ↓
            Controlador
            ↓
            método ejecutado
"""


class AdminDashboardUI(QWidget):

    #SEÑALES 

    productos_clicked = pyqtSignal() #señal que se emite cuando el usuario hace clic en el botón de PRODUCTOS
    personal_clicked = pyqtSignal() #señal que se emite cuando el usuario hace clic en el botón de PERSONAL
    cerrar_sesion = pyqtSignal() #señal que se emite cuando el usuario hace clic en el botón de CERRAR SESIÓN

    def __init__(self, sesion, parent=None):
        super().__init__(parent)
        self._sesion = sesion #la sesión del usuario administrador, que se utiliza para personalizar el saludo en el panel de administración

        #carga del archivo .ui que define el diseño del panel de administración
        ui_path = os.path.join(
            os.path.dirname(__file__),
            "../ui_pyqt/admin_dashboard.ui"
        )
        uic.loadUi(ui_path, self)

        #personalización dinámica del saludo del administrador
        self._setup_dynamic()

        #conexión de señales a los botones del panel de administración
        self._connect_signals()

    def _setup_dynamic(self):
        #este método personaliza dinámicamente el saludo del administrador en el panel de administración, 
        #utilizando el nombre de la sesión
        self.greeting_label.setText(f"HOLA {self._sesion.nombre}")

    def _connect_signals(self):
        #este método conecta las señales a los botones del panel de administración, 
        #para que cuando el usuario haga clic en ellos, se emitan las señales correspondientes


        self.logout_button.clicked.connect(
            #se emite la señal cerrar_sesion cuando el usuario hace clic en el botón de CERRAR SESIÓN
            lambda: self.cerrar_sesion.emit()
        )

        self.products_button.clicked.connect(
            #se emite la señal productos_clicked cuando el usuario hace clic en el botón de PRODUCTOS
            lambda: self.productos_clicked.emit()
        )

        self.staff_button.clicked.connect(
            #se emite la señal personal_clicked cuando el usuario hace clic en el botón de PERSONAL
            lambda: self.personal_clicked.emit()
        )