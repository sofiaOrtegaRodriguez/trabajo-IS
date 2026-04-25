from PyQt5.QtWidgets import QMessageBox

from src.vista.ui.auth_window import AuthUI
from src.vista.ui.carta_ui import CartaUI
from src.controlador.ControladorProductos import ControladorProductos


class MiVentana(AuthUI):
    def __init__(self):
        super().__init__()
        self._controlador = None
        self.carta_window = None
        self.login_requested.connect(self.on_button_click)
        self.register_requested.connect(self.on_register_click)

    def on_button_click(self, usuario, contrasena):
        if not self._controlador:
            self.show_login_error("No hay un controlador conectado.")
            return
        try:
            login_ok = self._controlador.comprobarLogin(usuario, contrasena)
        except Exception as exc:
            self.show_login_error("No se pudo conectar con la base de datos.")
            QMessageBox.critical(
                self,
                "Error de conexion",
                str(exc),
            )
            return

        if not login_ok:
            self.show_login_error("Usuario o contrasena incorrectos.")
            self.show_center_popup("USUARIO O CONTRASENA INCORRECTOS")
            return

        self._open_carta()

    def lanzarAvisoLogin(self):
        self.show_login_error("Usuario o contrasena incorrectos.")
        self.show_center_popup("USUARIO O CONTRASENA INCORRECTOS")

    def on_register_click(self, nombre, usuario, contrasena):
        if not self._controlador:
            self.show_register_error("No hay un controlador conectado.")
            return
        try:
            self._controlador.registrarCliente(nombre, usuario, contrasena)
        except ValueError as exc:
            self.show_register_error(str(exc))
            return
        except Exception as exc:
            self.show_register_error("No se pudo registrar en la base de datos.")
            QMessageBox.critical(
                self,
                "Error de registro",
                str(exc),
            )
            return

        self._open_carta()

    def _open_carta(self):
        controlador_carta = ControladorProductos(self._controlador._modelo)
        self.carta_window = CartaUI(controlador=controlador_carta)
        self.carta_window.show()
        self.close()

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador
