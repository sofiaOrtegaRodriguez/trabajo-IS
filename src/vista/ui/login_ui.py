from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget


from src.vista.ui.auth_common import asset

"""
    Esta clase representa el formulario de inicio de sesión en la interfaz gráfica. 
    Hereda de QWidget y utiliza un archivo .ui (del Designer de Qt) para definir su diseño.
    Proporciona señales para indicar cuando se ha enviado el formulario o cuando se solicita cambiar a otra vista
    (por ejemplo, la vista de registro). Además, incluye métodos para cargar un logotipo, conectar señales a los botones
    y campos de entrada, mostrar mensajes de error y limpiar los campos del formulario.
    NO se realiza la validación de credenciales ni el inicio de sesión en esta clase.
    La validación y el inicio de sesión se realizan en el controlador correspondiente.
"""

class LoginForm(QWidget):

    #aqui se definen las señales que se emitirán cuando el usuario interactúe con el formulario
    submitted = pyqtSignal() #esta señal se emite cuando el usuario hace clic en el botón de enviar o presiona Enter en el campo de contraseña
    switch_requested = pyqtSignal() #esta señal se emite cuando el usuario hace clic en el botón de cambiar a la vista de registro

    def __init__(self, parent=None):
        super().__init__(parent)
        #se carga el archivo .ui que define el diseño del formulario de inicio de sesión
        ui_file = Path(__file__).resolve().parent.parent / "ui_pyqt" / "login_form.ui"
        uic.loadUi(str(ui_file), self)

        #se cargan el logotipo y se conectan las señales de los botones y campos de entrada a los métodos correspondientes
        self._load_logo()
        self._connect_signals()

    #se carga el logotipo desde varios formatos de archivo (png, jpeg) y se establece en el QLabel correspondiente
    def _load_logo(self):
        logo_path = (
            asset("logos", "sushule_logo_circulo.png")
            or asset("logos", "sushule_logo.png")
            or asset("logos", "sushule_logo.jpeg")
        )

        if logo_path:
            pixmap = QPixmap(logo_path)

            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.logo_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.logo_label.setPixmap(scaled)

    #se conectan las señales de los botones y campos de entrada a los métodos correspondientes
    def _connect_signals(self):
        self.submit_button.clicked.connect(
            #cuando se hace clic en el botón de enviar, se emite la señal submitted para indicar que se ha enviado el formulario
            self.submitted.emit
        )

        self.switch_button.clicked.connect(
            #cuando se hace clic en el botón de cambiar a la vista de registro, se emite la señal switch_requested
            self.switch_requested.emit
        )

        self.pass_input.returnPressed.connect(
            #cuando se presiona Enter en el campo de contraseña, se emite la señal submitted para indicar que se ha enviado el formulario
            self.submitted.emit
        )

    #mostra un mensaje de error en el QLabel correspondiente y lo hace visible
    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
    #limpia los campos de usuario y contraseña, y oculta el QLabel de error
    def clear_fields(self):
        self.user_input.clear()
        self.pass_input.clear()
        self.error_label.hide()