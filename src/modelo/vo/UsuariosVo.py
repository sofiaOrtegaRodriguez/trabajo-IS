class UsuariosVo:
    def __init__(self, id_cliente, nombre, correo, puntos, fecha_cuenta):
        self.__id_cliente = id_cliente
        self.__nombre = nombre
        self.__correo = correo
        self.__puntos = puntos
        self.__fecha_cuenta = fecha_cuenta

    @property
    def id_cliente(self):
        return self.__id_cliente

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def puntos(self):
        return self.__puntos

    @property
    def fecha_cuenta(self):
        return self.__fecha_cuenta
