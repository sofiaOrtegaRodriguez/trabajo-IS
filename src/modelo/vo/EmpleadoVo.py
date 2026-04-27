class EmpleadoVo:
    def __init__(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        self.__id_empleado = id_empleado
        self.__ssn = ssn
        self.__usuario = usuario
        self.__correo = correo
        self.__contrasena = contrasena
        self.__tipo = tipo

    @property
    def id_empleado(self):
        return self.__id_empleado

    @property
    def ssn(self):
        return self.__ssn

    @property
    def usuario(self):
        return self.__usuario

    @property
    def nombre(self):
        return self.__usuario

    @property
    def correo(self):
        return self.__correo

    @property
    def contrasena(self):
        return self.__contrasena

    @property
    def tipo(self):
        return self.__tipo
