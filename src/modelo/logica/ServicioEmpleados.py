from src.modelo.dao.EmpleadoDaoJDBC import EmpleadoDaoJDBC


class ServicioEmpleados:
    def listarEmpleados(self):
        return EmpleadoDaoJDBC().listar()

    def crearEmpleado(self, ssn, usuario, correo, contrasena, tipo):
        return EmpleadoDaoJDBC().crear(ssn, usuario, correo, contrasena, tipo)

    def crearEmpleadoValidado(self, ssn, usuario, correo, contrasena, tipo):
        ssn = str(ssn).strip()
        usuario = str(usuario).strip()
        correo = str(correo).strip()
        contrasena = str(contrasena)
        tipo = str(tipo).strip()
        if len(ssn) != 11 or not ssn.isdigit():
            raise ValueError("El SSN debe tener 11 digitos.")
        if not usuario:
            raise ValueError("El usuario es obligatorio.")
        if not correo or "@" not in correo:
            raise ValueError("El correo no es valido.")
        if not contrasena:
            raise ValueError("La contrasena es obligatoria.")
        if not tipo:
            raise ValueError("El tipo de empleado es obligatorio.")
        return self.crearEmpleado(ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        return EmpleadoDaoJDBC().actualizar(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleadoValidado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        return self._actualizar_empleado_validado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def _actualizar_empleado_validado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        ssn = str(ssn).strip()
        usuario = str(usuario).strip()
        correo = str(correo).strip()
        contrasena = str(contrasena)
        tipo = str(tipo).strip()
        if len(ssn) != 11 or not ssn.isdigit():
            raise ValueError("El SSN debe tener 11 digitos.")
        if not usuario:
            raise ValueError("El usuario es obligatorio.")
        if not correo or "@" not in correo:
            raise ValueError("El correo no es valido.")
        if not contrasena:
            raise ValueError("La contrasena es obligatoria.")
        if not tipo:
            raise ValueError("El tipo de empleado es obligatorio.")
        return self.actualizarEmpleado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def eliminarEmpleado(self, id_empleado):
        return EmpleadoDaoJDBC().eliminar(id_empleado)

    def obtenerTiposEmpleado(self):
        return ["CAJERO", "COCINA"]

    def obtenerCategoriasAdmin(self):
        return ["Sushi", "Fritos", "Postres", "Bebidas"]
