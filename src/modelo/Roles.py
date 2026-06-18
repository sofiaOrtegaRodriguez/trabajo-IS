from abc import ABC, abstractmethod

# clase abstracta que define la estructura común de todos los roles del sistema

class Rol(ABC):
    @property
    @abstractmethod
    def nombre(self) -> str:
        # cada rol debe devolver su nombre identificador
        pass

    @property
    @abstractmethod
    def pantalla_inicial(self) -> str:
        """Devuelve un identificador abstracto de pantalla para la vista."""
        # cada rol debe devolver la pantalla a la que redirige al iniciar sesión
        pass

    @property
    def permite_puntos(self) -> bool:
        """Por defecto, los empleados no acumulan puntos de fidelidad."""
        # el único rol que acumula puntos es el cliente
        return False

# rol asignado a clientes

class RolCliente(Rol):
    nombre = "CLIENTE"
    pantalla_inicial = "CARTA" # el cliente una vez iniciado sesión entra directamente en carta
    
    @property
    def permite_puntos(self) -> bool: 
        return True #El cliente es el único rol que acumula puntos de fidelidad

# rol asignado a los cajeros
class RolCajero(Rol):
    nombre = "CAJERO"
    pantalla_inicial = "VENTANA_CAJERO" # el cajero una vez iniciado sesión entra directamente en la ventana del cajero


#rol asignado a los empleados de cocina
class RolCocina(Rol):
    nombre = "COCINA"
    pantalla_inicial = "VENTANA_COCINA" # el cajero una vez iniciado sesión entra direcatament een la ventana de cocina

# rol asignado al administrador
class RolAdministrador(Rol):
    nombre = "ADMINISTRADOR"
    pantalla_inicial = "VENTANA_ADMINISTRADOR" # el admin una vez iniciado sesuón entra directamente en la ventana de admin

# rol asignado al gerente
class RolGerente(Rol):
    nombre = "GERENTE"
    pantalla_inicial = "VENTANA_GERENTE" # el gerente una vez iniciado sesión entra directamente en la ventana del gerente
