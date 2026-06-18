# controlador que gestiona las operaaciones relacionadas con los empleados
# actúa de intermediario entre la vista y el modelo, sin contener lógica propia

class ControladorEmpleados:

    # recibe la referencia al modelo para poder llamar a su lógica de negocio
    def __init__(self, ref_modelo):
        self._modelo = ref_modelo # guardamos el modelo para usarlo en todas las oepraciones
        self._empleado_en_edicion_id = None

   
    # solicita al modelo la lista completa de los empleadks y la devuelve a vista
    def listarEmpleados(self):
        return self._modelo.listarEmpleados() 

    
    # recibe los datos del nuevo empleado desde la vista y los pasa al modelo para insertarlas en la BD
    def crearEmpleado(self, ssn, usuario, correo, contrasena, tipo):
        return self._modelo.crearEmpleadoValidado(ssn, usuario, correo, contrasena, tipo)



    # recibe el id del empleado a modificar y sus datos nuevos, los pasa al modelo para actualizarlos a la BD
    def actualizarEmpleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        return self._modelo.actualizarEmpleadoValidado(id_empleado, ssn, usuario, correo, contrasena, tipo)


    # recibe el id del empleado a eliminar y lo pasa al modelo para borrarlo de la BD
    def eliminarEmpleado(self, id_empleado):
        return self._modelo.eliminarEmpleado(id_empleado)

    def obtenerTiposEmpleado(self):
        return self._modelo.obtenerTiposEmpleado()

    def iniciarEdicionEmpleado(self, empleado):
        self._empleado_en_edicion_id = getattr(empleado, "id_empleado", None)
        return self._empleado_en_edicion_id

    def limpiarEdicionEmpleado(self):
        self._empleado_en_edicion_id = None
