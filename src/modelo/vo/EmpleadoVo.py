class EmpleadoVo:
    def __init__(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        self.__id_empleado = id_empleado #Id unico del empleado, generado por la base de datos
        self.__ssn = ssn #Numero de seguridad social del empleado
        self.__usuario = usuario #Nombre de usuario del empleado
        self.__correo = correo #Correo del empleado
        self.__contrasena = contrasena #Contraseña del empleado
        self.__tipo = tipo #Tipo de empleado (cajero, cocina, gerente, administrador)

    @property
    def id_empleado(self):
        """Devuelve el id único del empleado."""
        return self.__id_empleado

    @property
    def ssn(self):
        """Devuelve el número de seguridad social del empleado."""
        return self.__ssn

    @property
    def usuario(self):
        """Devuelve el nombre de usuario del empleado."""
        return self.__usuario

    @property
    def nombre(self):
        """Devuelve el nombre del empleado."""
        return self.__usuario

    @property
    def correo(self):
        """Devuelve el correo del empleado."""
        return self.__correo

    @property
    def contrasena(self):
        """Devuelve la contraseña del empleado."""
        return self.__contrasena

    @property
    def tipo(self):
        """Devuelve el tipo de empleado."""
        return self.__tipo
