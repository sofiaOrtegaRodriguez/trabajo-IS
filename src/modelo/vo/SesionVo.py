# clase que representa la sesión activa de un usuario tras hacer el login.
# guarda todos sus datos personales y su rol, que determina a qué pantallas puede acceder

from src.modelo.Factoría_Rol import Factoria_Rol

class SesionVo:
    def __init__(self, id_sesion, nombre, correo, puntos=0, fecha_cuenta=None, rol="cliente"):
        self.__id_sesion = id_sesion # identificador único del usuario en la BD
        self.__nombre = nombre # nombre del usuario
        self.__correo = correo # correo del usuario
        self.__puntos = int(puntos or 0) # puntos del usuario (0 si no tiene)
        self.__fecha_cuenta = fecha_cuenta # fecha de creación de la cuenta
        # usamos la Factoría_Rol para obtener el objeto de rol correspondiete según el tipo de usuario
        # este objeto determina su pantalla inicial y si puede acumular puntos (patrón estrategia)
        self.__rol_objeto = Factoria_Rol(rol).get_rol()

    @property
    def id_sesion(self):
        return self.__id_sesion # devuelve el id de la sesión

    @property
    def id_cliente(self):
        return self.__id_sesion # alias de id_sesion para cuando se usa en contexto de cliente

    @property
    def id_empleado(self):
        return self.__id_sesion # alias de id_sesion para cuando se usa en contexto de empleado

    @property
    def nombre(self):
        return self.__nombre # devuelve nombre de usuario

    @property
    def correo(self):
        return self.__correo # devuelve el correo del usuario
 
    @property
    def puntos(self):
        return self.__puntos # devuelve los puntos del usuario
 
    @property
    def fecha_cuenta(self):
        return self.__fecha_cuenta # devuelve la fecha en la que fue creada la cuenta


    # devuelve el objeto de rol completo (RolCliente, RolCajero etc.)
    # este objeto contiene la pantalla inicial y si permite puntos (patrón estrategia)
    @property
    def rol(self):
        """Devuelve la estrategia de rol completa."""
        return self.__rol_objeto

    
    # devuelve True si el usuario tiene rol de cliente
    @property
    def es_cliente(self):
        return self.__rol_objeto.nombre == "CLIENTE"

    # devuelve True si el usuario tiene rol de cajero
    @property
    def es_cajero(self):
        return self.__rol_objeto.nombre == "CAJERO"
 
    # devuelve True si el usuario tiene rol de cocina
    @property
    def es_cocina(self):
        return self.__rol_objeto.nombre == "COCINA"
    
    # devuelve True si el usuario tiene rol de gerente
    @property
    def es_gerente(self):
        return self.__rol_objeto.nombre == "GERENTE"

    # devuelve True si el usuario tiene rol de administrador
    @property
    def es_administrador(self):
        return self.__rol_objeto.nombre == "ADMINISTRADOR"

    # devuelve True si el rol del usuario permite acumular puntos (solo cliente)
    @property
    def permite_puntos(self):
        return self.__rol_objeto.permite_puntos

    # establece los puntos del usuario, jamás en negativo
    def set_puntos(self, puntos):
        self.__puntos = max(0, int(puntos or 0))

    # suma los puntos al usuario; solo funciona si es cliente
    def sumar_puntos(self, puntos):
        if not self.es_cliente: # si no es cliente no hace nada
            return
        self.__puntos += max(0, int(puntos or 0)) # se suman los puntos, nunca negativos

    # resta puntos al usuario al canjearlos; solo funciona si son clientes y nunca baja del 0
    def consumir_puntos(self, puntos):
        if not self.es_cliente: # si no es cliente no hace nada
            return
        self.__puntos = max(0, self.__puntos - max(0, int(puntos or 0))) # se restan los puntos sin llegar a d0