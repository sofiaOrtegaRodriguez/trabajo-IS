from src.modelo.dao.EmpleadoDaoJDBC import EmpleadoDaoJDBC


class ServicioEmpleados:
    """
    Servicio de lógica de negocio para empleados.

    Capa intermedia entre el controlador y EmpleadoDaoJDBC.
    Responsabilidades:
      - Delegar operaciones CRUD en el DAO
      - Validar datos antes de persistirlos
      - Proveer listas de valores fijos (tipos de empleado, categorías)

    Mismo patrón que ServicioProductos y ServicioPromociones:
      - Sin validar (crearEmpleado, actualizarEmpleado): persistencia pura
      - Validado (crearEmpleadoValidado, actualizarEmpleadoValidado): valida + persiste
    """

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PÚBLICOS: CRUD
    # ─────────────────────────────────────────────────────────────

    def listarEmpleados(self):
        """
        Devuelve la lista de VOs de empleado tal como los entrega el DAO.
        Sin transformación adicional.
        """
        return EmpleadoDaoJDBC().listar()

    def crearEmpleado(self, ssn, usuario, correo, contrasena, tipo):
        """
        Crea un empleado en la BD SIN validar los datos.
        Pasa los parámetros directamente al DAO.
        """
        return EmpleadoDaoJDBC().crear(ssn, usuario, correo, contrasena, tipo)

    def crearEmpleadoValidado(self, ssn, usuario, correo, contrasena, tipo):
        """
        Valida los datos y, si son correctos, crea el empleado en la BD.
        Es el método que debe llamar el controlador cuando el usuario
        rellena el formulario y pulsa "Guardar" en modo creación.

        Lanza ValueError con mensaje descriptivo si algún dato no es válido.
        """
        # Normaliza todos los campos antes de validar
        ssn = str(ssn).strip()
        usuario = str(usuario).strip()
        correo = str(correo).strip()
        contrasena = str(contrasena)       # no se hace strip() para respetar espacios en contraseñas
        tipo = str(tipo).strip()

        # Validación del SSN: exactamente 11 dígitos numéricos
        if len(ssn) != 11 or not ssn.isdigit():
            raise ValueError("El SSN debe tener 11 digitos.")

        # Validación del usuario: no puede estar vacío
        if not usuario:
            raise ValueError("El usuario es obligatorio.")

        # Validación del correo: debe contener "@" como mínimo
        if not correo or "@" not in correo:
            raise ValueError("El correo no es valido.")

        # Validación de la contraseña: no puede estar vacía
        if not contrasena:
            raise ValueError("La contrasena es obligatoria.")

        # Validación del tipo: no puede estar vacío
        if not tipo:
            raise ValueError("El tipo de empleado es obligatorio.")

        return self.crearEmpleado(ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        """
        Actualiza un empleado en la BD SIN validar los datos.
        Necesita el id_empleado para identificar el registro en la BD.
        """
        return EmpleadoDaoJDBC().actualizar(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleadoValidado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        """
        Valida los datos y, si son correctos, actualiza el empleado en la BD.
        Es el método que debe llamar el controlador cuando el usuario
        edita un empleado y pulsa "Guardar cambios".

        Delega en _actualizar_empleado_validado (método privado) para
        separar la lógica de validación+actualización en un lugar único,
        lo que facilita reutilizarla sin exponer el método privado directamente.
        """
        return self._actualizar_empleado_validado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS: validación de actualización
    # ─────────────────────────────────────────────────────────────

    def _actualizar_empleado_validado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        """
        Valida los datos y actualiza el empleado en la BD.

        Las reglas de validación son idénticas a las de crearEmpleadoValidado.
        Se mantienen separadas (en lugar de extraerlas a un método común)
        por si en el futuro la edición requiere reglas distintas a la creación
        (por ejemplo, permitir contraseña vacía para "no cambiar la actual").
        """
        # Normaliza todos los campos antes de validar
        ssn = str(ssn).strip()
        usuario = str(usuario).strip()
        correo = str(correo).strip()
        contrasena = str(contrasena)
        tipo = str(tipo).strip()

        # Las mismas 5 reglas que en crearEmpleadoValidado
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

    # ─────────────────────────────────────────────────────────────
    # MÉTODO PÚBLICO: eliminación
    # ─────────────────────────────────────────────────────────────

    def eliminarEmpleado(self, id_empleado):
        """
        Elimina el empleado con el ID indicado.
        Delega directamente en el DAO sin validación adicional.
        """
        return EmpleadoDaoJDBC().eliminar(id_empleado)

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PÚBLICOS: valores fijos de configuración
    # ─────────────────────────────────────────────────────────────

    def obtenerTiposEmpleado(self):
        """
        Devuelve la lista de tipos de empleado válidos en la aplicación.
        Estos valores se usan para rellenar el combobox del formulario
        de gestión de personal.

        Son valores fijos definidos en el servicio (no en la BD) porque
        los roles de la aplicación están determinados por el diseño del sistema.
        """
        return ["CAJERO", "COCINA"]

    def obtenerCategoriasAdmin(self):
        """
        Devuelve la lista de categorías de producto válidas en la aplicación.
        Se usan para rellenar el combobox de categorías en el formulario
        de administración de productos.

        Al igual que los tipos de empleado, son valores fijos del dominio,
        no se consultan a la BD.
        """
        return ["Sushi", "Fritos", "Postres", "Bebidas"]