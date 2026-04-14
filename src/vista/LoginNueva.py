from PyQt5.QtWidgets import QMessageBox

from src.vista.ui.auth_window import AuthUI


class MiVentana(AuthUI):
    def __init__(self):
        super().__init__()
        self._controlador = None
        self.login_requested.connect(self.on_button_click)
        self.register_requested.connect(self.on_register_click)

    def on_button_click(self, usuario, contrasena):
        if not self._controlador:
            self.show_login_error("No hay un controlador conectado.")
            return
        try:
            self._controlador.comprobarLogin(usuario, contrasena)
        except Exception as exc:
            self.show_login_error("No se pudo conectar con la base de datos.")
            QMessageBox.critical(
                self,
                "Error de conexion",
                str(exc),
            )

    def lanzarAvisoLogin(self):
        self.show_login_error("Usuario o contraseña incorrectos.")
        QMessageBox.warning(
            self,
            "Inicio de sesión",
            "No se ha podido iniciar sesión con esas credenciales.",
        )

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

        QMessageBox.information(
            self,
            "Registro completado",
            "Tu cuenta se ha creado correctamente. Ya puedes iniciar sesion.",
        )
        self.show_login()

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador
