class UserDao:
    def select(self):
        raise NotImplementedError("Metodo select() no implementado")

    def consultarLogin(self, login_vo):
        raise NotImplementedError("Metodo consultarLogin() no implementado")

    def registrarCliente(self, nombre, correo, contrasena):
        raise NotImplementedError("Metodo registrarCliente() no implementado")

    def actualizarPuntos(self, id_cliente, puntos):
        raise NotImplementedError("Metodo actualizarPuntos() no implementado")
