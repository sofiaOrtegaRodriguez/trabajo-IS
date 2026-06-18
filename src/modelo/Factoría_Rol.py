from src.modelo.Roles import RolCliente, RolCajero, RolCocina, RolAdministrador, RolGerente


class Factoria_Rol:
    def __init__(self, nombre_rol: str):
        """Factory de roles para resolver la estrategia del usuario."""
        self.nombre_norm = str(nombre_rol).strip().lower()
        self.roles = {
            "cliente": RolCliente(),
            "cajero": RolCajero(),
            "cocina": RolCocina(),
            "administrador": RolAdministrador(),
            "gerente": RolGerente(),
        }

    def get_rol(self):
        """Devuelve el objeto de rol correspondiente al nombre dado."""
        return self.roles.get(self.nombre_norm, RolCliente())
