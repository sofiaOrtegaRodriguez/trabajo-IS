class SesionVo:
    def __init__(self, id_sesion, nombre, correo, puntos=0, fecha_cuenta=None, rol="cliente"):
        self.__id_sesion = id_sesion
        self.__nombre = nombre
        self.__correo = correo
        self.__puntos = int(puntos or 0)
        self.__fecha_cuenta = fecha_cuenta
        self.__rol = rol

    @property
    def id_sesion(self):
        return self.__id_sesion

    @property
    def id_cliente(self):
        return self.__id_sesion

    @property
    def id_empleado(self):
        return self.__id_sesion

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

    @property
    def rol(self):
        return self.__rol

    @property
    def es_cliente(self):
        return self.__rol == "cliente"

    @property
    def es_cajero(self):
        return self.__rol == "cajero"

    @property
    def es_gerente(self):
        return self.__rol == "gerente"

    @property
    def es_administrador(self):
        return self.__rol == "administrador"

    @property
    def permite_puntos(self):
        return self.es_cliente

    def set_puntos(self, puntos):
        self.__puntos = max(0, int(puntos or 0))

    def sumar_puntos(self, puntos):
        if not self.es_cliente:
            return
        self.__puntos += max(0, int(puntos or 0))

    def consumir_puntos(self, puntos):
        if not self.es_cliente:
            return
        self.__puntos = max(0, self.__puntos - max(0, int(puntos or 0)))
