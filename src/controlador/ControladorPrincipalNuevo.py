from src.modelo.vo.LoginVo import LoginVo


class ControladorPrincipal:
    def __init__(self, ref_vista, ref_modelo):
        self._vista = ref_vista
        self._modelo = ref_modelo

    def ventanaIniciarSesion(self):
        if hasattr(self._vista, "clear_fields"):
            self._vista.clear_fields()
        self._vista.show()

    def __getattr__(self, name):
        if name.startswith("ventanaIniciarSesi"):
            return self.ventanaIniciarSesion
        raise AttributeError(name)

    def comprobarLogin(self, nombre, passw):
        login = LoginVo(nombre, passw)
        resultado = self._modelo.comprobarLogin(login)

        if resultado is None:
            self._vista.lanzarAvisoLogin()
            return

        self._vista.close()

    def registrarCliente(self, nombre, correo, contrasena):
        self._modelo.registrarCliente(nombre, correo, contrasena)
