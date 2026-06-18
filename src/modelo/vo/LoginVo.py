class LoginVo:
    def __init__(self, correo, contrasena, nombre=None):
        self.__correo = correo #Correo del usuario
        self.__contrasena = contrasena #Contraseña del usuario
        self.__nombre = nombre #Nombre del usuario, opcional ya que solo se usa para el registro
    
    @property
    def correo(self):
        """Devuelve el correo del usuario."""
        return self.__correo

    @property
    def contrasena(self):
        """Devuelve la contraseña del usuario."""
        return self.__contrasena
    
    @property
    def nombre(self):
        """Devuelve el nombre del usuario."""
        return self.__nombre
