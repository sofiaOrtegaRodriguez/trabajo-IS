from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.dao.EmpleadoDaoJDBC import EmpleadoDaoJDBC
from src.modelo.vo.LoginVo import LoginVo


class ServicioAuth:
    def comprobarLogin(self, loginVo):
        """Comprueba las credenciales de inicio de sesión en el Dao y devuelve la sesión correspondiente 
        si son válidas."""
        login_dao = UserDaoJDBC()
        sesion = login_dao.consultarLogin(loginVo)
        if sesion is not None: #Si la sesion es de un cliente, se devuelve directamente
            return sesion
        empleado_dao = EmpleadoDaoJDBC() #Si es None, se comprueba si es un empleado
        return empleado_dao.consultarLogin(loginVo)

    def comprobarLoginValidado(self, correo, contrasena):
        """Valida que correo y contraseña estén completos y se lo pasa al método de comprobación en un LoginVo."""
        correo = str(correo).strip()
        contrasena = str(contrasena)
        if not correo or not contrasena:
            raise ValueError("Completa correo y contrasena.")
        
        return self.comprobarLogin(LoginVo(correo, contrasena))

    def registrarCliente(self, registroVo):
        """Registra un nuevo cliente en el Dao."""
        login_dao = UserDaoJDBC()
        return login_dao.registrarCliente(registroVo)

    def registrarClienteValidado(self, nombre, correo, contrasena):
        """Valida que nombre, correo y contraseña estén completos y se lo pasa al método de registro en un LoginVo.
        Luego, intenta autenticar al nuevo cliente y devuelve la sesión si es exitosa."""
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
