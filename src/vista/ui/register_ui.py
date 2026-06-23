from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from src.vista.ui.auth_common import asset


"""
 Esta clase representa el formulario de registro de usuario en la interfaz gráfica.
 Hereda de QWidget y utiliza un archivo .ui (del Designer de Qt) para definir su diseño.
 Proporciona señales para indicar cuando se ha enviado el formulario o cuando se solicita cambiar a otra vista 
 (por ejemplo, la vista de inicio de sesión). Además, incluye métodos para cargar un logotipo, conectar señales a los botones 
 y campos de entrada, mostrar mensajes de error y limpiar los campos del formulario.
"""

"""
 NO se crean usuarios ni se valida la información en esta clase. 
 La validación y creación de usuarios se realiza en el controlador correspondiente.
"""
class RegisterForm(QWidget):

    #aqui se definen las señales que se emitirán cuando el usuario interactúe con el formulario
    submitted = pyqtSignal() #esta señal se emite cuando el usuario hace clic en el botón de enviar o presiona Enter en el campo de confirmación de contraseña
    switch_requested = pyqtSignal() #esta señal se emite cuando el usuario hace clic en el botón de cambiar a la vista de inicio de sesión

    def __init__(self, parent=None):
        super().__init__(parent) #hereda del constructor de QWidget y establece el widget padre si se proporciona

        #carga el archivo .ui que define el diseño del formulario de registro
        ui_file = (
            Path(__file__).resolve().parent.parent
            / "ui_pyqt"
            / "register_form.ui"
        )

        #carga el diseño del archivo .ui en la instancia actual de RegisterForm
        uic.loadUi(str(ui_file), self)
        self._load_logo() #añade el logotipo al formulario
        self._connect_signals() #conecta las señales de los botones y campos de entrada a los métodos correspondientes

    def _load_logo(self):
        #en este método se intenta cargar el logotipo desde varios formatos de archivo (png, jpeg) y se establece en el QLabel correspondiente

        #se busca el logotipo en la carpeta de assets/logos y se intenta cargar en el QLabel del formulario
        logo_path = (
            asset("logos", "sushule_logo_circulo.png")
            or asset("logos", "sushule_logo.png")
            or asset("logos", "sushule_logo.jpeg")
        )
        #si se encuentra un logotipo válido, se carga en el QLabel y se ajusta su tamaño manteniendo la proporción
        if logo_path:
            pixmap = QPixmap(logo_path)
            #si el pixmap no está vacío, se establece en el QLabel y se escala para mantener la proporción y suavizar la transformación
            if not pixmap.isNull():
                self.logo_label.setPixmap(
                    pixmap.scaled(
                        self.logo_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )

    #conecta las señales de los botones y campos de entrada a los métodos correspondientes
    def _connect_signals(self):

        #SUBMIT BUTTON:
        #el botón de enviar y el campo de confirmación de contraseña emiten
        #la señal submitted cuando se hace clic o se presiona Enter, respectivamente
        self.submit_button.clicked.connect(
            self.submitted.emit
        )
        #el campo de confirmación de contraseña emite la señal submitted cuando se presiona Enter
        self.confirm_input.returnPressed.connect(
            self.submitted.emit
        )

        #SWITCH BUTTON:
        self.switch_button.clicked.connect(
            #cuando se hace clic en el botón de cambiar a la vista de inicio de sesión, se emite la señal switch_requested
            self.switch_requested.emit
        )

    #Mostrar un mensaje de error en el formulario de registro. 
    # Este método establece el texto del QLabel de error y lo hace visible.
    def show_error(self, message):
        self.error_label.setText(message) #establece el mensaje de error en el QLabel correspondiente
        self.error_label.show() #lo hace visible para que el usuario pueda verlo

    #Limpia los campos de entrada del formulario de registro y oculta el mensaje de error.
    def clear_fields(self):
        self.name_input.clear()
        self.user_input.clear()
        self.pass_input.clear()
        self.confirm_input.clear()
        self.error_label.hide()