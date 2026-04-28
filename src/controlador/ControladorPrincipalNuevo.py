from src.modelo.vo.LoginVo import LoginVo


class ControladorPrincipal:
    def __init__(self, ref_vista, ref_modelo):
        self._vista = ref_vista
        self._modelo = ref_modelo
        self._sesion_actual = None

    def ventanaIniciarSesion(self):
        if hasattr(self._vista, "clear_fields"):
            self._vista.clear_fields()
        self._vista.show()

    def __getattr__(self, name):
        if name.startswith("ventanaIniciarSesi"):
            return self.ventanaIniciarSesion
        raise AttributeError(name)

    def autenticar_usuario(self, nombre, passw):
        login = LoginVo(nombre, passw)
        resultado = self._modelo.comprobarLogin(login)
        self._sesion_actual = resultado if resultado is not None else None
        return resultado

    def registrar_cliente(self, nombre, correo, contrasena):
        self._modelo.registrarCliente(nombre, correo, contrasena)
        return self.autenticar_usuario(correo, contrasena)

    def comprobarLogin(self, nombre, passw):
        return self.autenticar_usuario(nombre, passw)

    def registrarCliente(self, nombre, correo, contrasena):
        return self.registrar_cliente(nombre, correo, contrasena)

    def get_modelo(self):
        return self._modelo

    def get_cliente(self):
        return self._sesion_actual

    def get_sesion(self):
        return self._sesion_actual
