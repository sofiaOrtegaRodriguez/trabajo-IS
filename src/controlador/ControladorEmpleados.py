class ControladorEmpleados:
    """
    Fachada entre ControladorAdmin y el modelo para la gestión de empleados.
    No contiene lógica propia; delega todo en self._modelo.
    """

    def __init__(self, ref_modelo):
        self._modelo = ref_modelo
        self._empleado_en_edicion_id = None  # Id del empleado en edición (None = modo creación)

    def listarEmpleados(self):
        return self._modelo.listarEmpleados()

    def crearEmpleado(self, ssn, usuario, correo, contrasena, tipo):
        return self._modelo.crearEmpleadoValidado(ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        return self._modelo.actualizarEmpleadoValidado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def eliminarEmpleado(self, id_empleado):
        return self._modelo.eliminarEmpleado(id_empleado)

    def obtenerTiposEmpleado(self):
        """Lista de roles/tipos disponibles para poblar el ComboBox de la vista."""
        return self._modelo.obtenerTiposEmpleado()

    def iniciarEdicionEmpleado(self, empleado):
        """
        Guarda el id del empleado que se va a editar.
        ControladorAdmin lo consulta en _on_guardar_empleado si la vista no propaga el id.
        """
        self._empleado_en_edicion_id = getattr(empleado, "id_empleado", None)
        return self._empleado_en_edicion_id

    def limpiarEdicionEmpleado(self):
        """Resetea el estado de edición → el siguiente guardar será una creación."""
        self._empleado_en_edicion_id = None