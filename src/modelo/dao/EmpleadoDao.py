class EmpleadoDao:
    def consultarLogin(self, login_vo):
        raise NotImplementedError("Metodo consultarLogin() no implementado")

    def listar(self):
        raise NotImplementedError("Metodo listar() no implementado")

    def crear(self, ssn, usuario, correo, contrasena, tipo):
        raise NotImplementedError("Metodo crear() no implementado")

    def actualizar(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        raise NotImplementedError("Metodo actualizar() no implementado")

    def eliminar(self, id_empleado):
        raise NotImplementedError("Metodo eliminar() no implementado")
