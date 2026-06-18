from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.dao.EmpleadoDaoJDBC import EmpleadoDaoJDBC
from src.modelo.vo.LoginVo import LoginVo


class ServicioAuth:
    def comprobarLogin(self, loginVo):
        login_dao = UserDaoJDBC()
        sesion = login_dao.consultarLogin(loginVo)
        if sesion is not None:
            return sesion
        empleado_dao = EmpleadoDaoJDBC()
        return empleado_dao.consultarLogin(loginVo)

    def comprobarLoginValidado(self, correo, contrasena):
        correo = str(correo).strip()
        contrasena = str(contrasena)
        if not correo or not contrasena:
            raise ValueError("Completa correo y contrasena.")
        
        return self.comprobarLogin(LoginVo(correo, contrasena))

    def registrarCliente(self, registroVo):
        login_dao = UserDaoJDBC()
        return login_dao.registrarCliente(registroVo)

    def registrarClienteValidado(self, nombre, correo, contrasena):
        nombre = str(nombre).strip()
        correo = str(correo).strip()
        contrasena = str(contrasena)
        if not nombre or not correo or not contrasena:
            raise ValueError("Rellena todos los campos.")
        
        registro = LoginVo(correo, contrasena, nombre)
        self.registrarCliente(registro)
        resultado = self.comprobarLogin(LoginVo(correo, contrasena))
        if resultado is None:
            raise ValueError("No se pudo autenticar la nueva cuenta.")
        return resultado
