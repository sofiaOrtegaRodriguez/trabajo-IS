class ControladorEmpleados:
    def __init__(self, ref_modelo):
        self._modelo = ref_modelo

    def listarEmpleados(self):
        return self._modelo.listarEmpleados()

    def crearEmpleado(self, ssn, usuario, correo, contrasena, tipo):
        return self._modelo.crearEmpleado(ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        return self._modelo.actualizarEmpleado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def eliminarEmpleado(self, id_empleado):
        return self._modelo.eliminarEmpleado(id_empleado)
