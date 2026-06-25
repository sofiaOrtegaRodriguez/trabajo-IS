"""
ControladorAdmin
Responsabilidad:
- Gestiona todas las acciones de la pantalla del Administrador.
- Construye, conecta y destruye las sub-vistas de su rol.
- Actúa de intermediario entre las vistas del admin y el modelo.
- No contiene lógica de negocio propia; delega en el modelo.
"""

class ControladorAdmin:

    def __init__(self, ref_modelo, ref_vista_principal, ref_controlador_productos, ref_controlador_empleados):
        """
        Constructor. Recibe por inyección de dependencias:
          - ref_modelo             → la capa de lógica/negocio global
          - ref_vista_principal    → VentanaPrincipal (para mostrar widgets, pedir confirmaciones…)
          - ref_controlador_productos  → ControladorProductos (sub-controlador delegado)
          - ref_controlador_empleados  → ControladorEmpleados (sub-controlador delegado)

        Ninguna lógica de negocio aquí: solo inicialización de referencias internas.
        """
        self._modelo = ref_modelo
        self._vista = ref_vista_principal               # VentanaPrincipal
        self._ctrl_productos = ref_controlador_productos
        self._ctrl_empleados = ref_controlador_empleados
        self._producto_editando = None  # Nombre del producto en edición (None = modo creación)

        # ── Referencias a sub-vistas activas ──────────────────────────────────
        # Se almacenan para poder cerrarlas al navegar o cerrar sesión.
        self._admin_dashboard_widget = None
        self._admin_productos_widget = None
        self._admin_personal_widget = None

        # ── Fábricas de vistas ────────────────────────────────────────────────
        # Callables que construyen cada sub-vista. Se inyectan desde VentanaPrincipal
        # para que este controlador no importe PyQt5 directamente (respeta MVC).
        self._fabrica_dashboard = None
        self._fabrica_productos = None
        self._fabrica_personal = None

    # ── Inyección de fábricas de vistas ──────────────────────────────────────

    def set_fabricas_vistas(self, fabrica_dashboard, fabrica_productos, fabrica_personal):
        """
        VentanaPrincipal llama a este método justo después de crear el controlador
        para pasarle las funciones (lambdas o métodos) que instancian cada sub-vista.
        Así el controlador nunca importa clases Qt — solo llama a estas fábricas.
        """
        self._fabrica_dashboard = fabrica_dashboard
        self._fabrica_productos = fabrica_productos
        self._fabrica_personal = fabrica_personal

    # ── Navegación ────────────────────────────────────────────────────────────
    # Estos tres métodos controlan qué pantalla se muestra dentro del área admin.
    # Patrón común:
    #   1. Cierra sub-vistas anteriores (_close_admin_children)
    #   2. Crea la nueva sub-vista mediante la fábrica correspondiente
    #   3. Conecta las señales de la vista a los manejadores internos (_on_*)
    #   4. Carga datos iniciales si son necesarios
    #   5. Pide a VentanaPrincipal que muestre el widget

    def ir_dashboard(self):
        """
        Navega al dashboard del administrador.
        Solo conecta botones de navegación (ir a productos / personal) y cierre de sesión.
        No carga datos de BD porque el dashboard es meramente de bienvenida/menú.
        """
        self._close_admin_children()
        sesion = self._vista.get_sesion_actual()          # Datos del empleado logueado
        dashboard = self._fabrica_dashboard(sesion)
        dashboard.productos_clicked.connect(self.ir_productos)
        dashboard.personal_clicked.connect(self.ir_personal)
        dashboard.cerrar_sesion.connect(self._confirmar_cerrar_sesion)
        self._admin_dashboard_widget = dashboard
        self._vista.mostrar_widget(dashboard)

    def ir_productos(self):
        """
        Navega a la pantalla de gestión de productos (CRUD + promociones).
        Conecta todas las señales de la vista de productos a sus manejadores.
        Tras conectar, activa modo creación y carga los datos actuales de BD.
        """
        self._close_admin_children()
        ventana = self._fabrica_productos()
        # Señales de navegación y CRUD de productos
        ventana.volver_menu.connect(self.ir_dashboard)
        ventana.editar_producto_requested.connect(self._on_editar_producto)
        ventana.guardar_producto_requested.connect(self._on_guardar_producto)
        ventana.eliminar_producto_requested.connect(self._on_confirmar_eliminar_producto)
        # Señales de CRUD de promociones
        ventana.guardar_promocion_requested.connect(self._on_guardar_promocion)
        ventana.eliminar_promocion_requested.connect(self._on_eliminar_promocion)
        self._admin_productos_widget = ventana
        ventana.activar_modo_creacion()                        # Formulario vacío, listo para crear
        self._cargar_admin_productos_en_vista(ventana)        # Llena tabla de productos y promociones
        self._vista.mostrar_widget(ventana)
        self._vista.adjustSize()

    def ir_personal(self):
        """
        Navega a la pantalla de gestión de personal (CRUD de empleados).
        Igual que ir_productos pero para la sub-vista de personal.
        También inicializa el combo de tipos de empleado.
        """
        self._close_admin_children()
        sesion = self._vista.get_sesion_actual()
        ventana = self._fabrica_personal(sesion)
        ventana.volver_menu.connect(self.ir_dashboard)
        ventana.editar_empleado_requested.connect(self._on_editar_empleado)
        ventana.guardar_empleado_requested.connect(self._on_guardar_empleado)
        ventana.eliminar_empleado_requested.connect(self._on_confirmar_eliminar_empleado)
        ventana.cerrar_sesion.connect(self._confirmar_cerrar_sesion)
        self._cargar_personal_en_vista(ventana)               # Llena la tabla de empleados
        ventana.inicializar_tipos(self.obtener_tipos_empleado())  # Popula el ComboBox de roles
        ventana.activar_modo_creacion()
        self._admin_personal_widget = ventana
        self._vista.mostrar_widget(ventana)
        self._vista.adjustSize()

    # ── Productos — métodos de fachada hacia ControladorProductos ─────────────
    # Estos métodos son la "API" que el controlador Admin expone internamente.
    # Delegan en _ctrl_productos sin añadir lógica propia.

    def obtener_schema_productos(self):
        """Devuelve el schema de la tabla PRODUCTOS (ej: si tiene columna de categoría)."""
        return self._ctrl_productos.describirProductos()

    def obtener_categorias(self):
        """Lista de categorías válidas para el formulario de producto."""
        return self._ctrl_productos.obtenerCategoriasAdmin()

    def listar_productos(self):
        """Todos los productos de la BD como lista de ProductoVo."""
        return self._ctrl_productos.listarProductos()

    def listar_promociones(self):
        """Todas las promociones activas/registradas."""
        return self._ctrl_productos.listarPromociones()

    def preparar_promociones_vista(self, promociones=None):
        """Transforma los VOs de promoción al formato que espera la tabla de la vista."""
        return self._ctrl_productos.prepararPromocionesVista(promociones)

    def iniciar_edicion_producto(self, producto):
        """
        Guarda el nombre del producto que se va a editar.
        Se usa en guardar_producto para distinguir creación vs actualización.
        """
        self._producto_editando = getattr(producto, "nombre", None)

    def limpiar_edicion_producto(self):
        """Resetea el estado de edición → el siguiente guardar será una CREACIÓN."""
        self._producto_editando = None

    def guardar_producto(self, nombre, precio, ingredientes, disponible, stock, categoria):
        """
        Crea o actualiza un producto según el estado de _producto_editando:
          - None  → crearProducto  (nuevo registro en BD)
          - str   → actualizarProducto  (modifica el producto con ese nombre original)
        Limpia _producto_editando al terminar.
        """
        if self._producto_editando is None:
            self._ctrl_productos.crearProducto(nombre, precio, ingredientes, disponible, stock, categoria)
        else:
            self._ctrl_productos.actualizarProducto(
                self._producto_editando, nombre, precio, ingredientes, disponible, stock, categoria
            )
        self._producto_editando = None  # Siempre volvemos a modo creación tras guardar

    def eliminar_producto(self, nombre_producto):
        """
        Elimina un producto de la BD.
        Si era el que estaba en edición, limpia también esa referencia.
        """
        self._ctrl_productos.eliminarProducto(nombre_producto)
        if self._producto_editando == nombre_producto:
            self._producto_editando = None

    def guardar_promocion(self, datos):
        """
        Crea una nueva promoción. El dict `datos` viene directamente del formulario de la vista:
          - 'descuento'       → porcentaje (se castea a int)
          - 'fecha_inicio'    → string de fecha
          - 'fecha_fin'       → string de fecha
          - 'nombre_producto' → string (se limpia con strip)
        """
        self._ctrl_productos.crearPromocion(
            int(datos.get("descuento", 0)),
            datos.get("fecha_inicio"),
            datos.get("fecha_fin"),
            str(datos.get("nombre_producto", "")).strip(),
        )

    def eliminar_promocion(self, id_promocion):
        """Elimina la promoción con el id dado."""
        self._ctrl_productos.eliminarPromocion(id_promocion)

    # ── Personal — métodos de fachada hacia ControladorEmpleados ──────────────

    def listar_empleados(self):
        """Todos los empleados de la BD."""
        return self._ctrl_empleados.listarEmpleados()

    def obtener_tipos_empleado(self):
        """Tipos/roles de empleado disponibles (para poblar el ComboBox de la vista)."""
        return self._ctrl_empleados.obtenerTiposEmpleado()

    def iniciar_edicion_empleado(self, empleado):
        """Delega en ControladorEmpleados para guardar el empleado en edición."""
        return self._ctrl_empleados.iniciarEdicionEmpleado(empleado)

    def limpiar_edicion_empleado(self):
        """Resetea el estado de edición de empleado en el sub-controlador."""
        self._ctrl_empleados.limpiarEdicionEmpleado()

    def guardar_empleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        """
        Crea o actualiza un empleado:
          - id_empleado None  → crearEmpleado
          - id_empleado int   → actualizarEmpleado
        (Nota: este método está definido dos veces en el original;
         la segunda definición sobreescribe la primera — Python usa la última.)
        """
        if id_empleado is None:
            self._ctrl_empleados.crearEmpleado(ssn, usuario, correo, contrasena, tipo)
        else:
            self._ctrl_empleados.actualizarEmpleado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def eliminar_empleado(self, id_empleado):
        """Elimina un empleado por su id."""
        self._ctrl_empleados.eliminarEmpleado(id_empleado)

    # ── Manejadores internos — señales de la vista de PRODUCTOS ───────────────
    # Estos métodos son los receptores de las señales Qt emitidas por la vista.
    # Orquestan: validar → llamar fachada → actualizar vista → notificar otras capas.

    def _on_editar_producto(self, producto):
        """
        Señal: el usuario pulsó 'Editar' en la tabla de productos.
        1. Guarda el nombre del producto en _producto_editando.
        2. Pone el formulario en modo edición (rellena los campos con los datos del producto).
        """
        self.iniciar_edicion_producto(producto)
        if self._admin_productos_widget is not None:
            self._admin_productos_widget.activar_modo_edicion(producto)

    def _on_guardar_producto(self, nombre, precio, ingredientes, disponible, stock, categoria):
        """
        Señal: el usuario pulsó 'Guardar' en el formulario de producto.
        1. Llama a guardar_producto (crea o actualiza según _producto_editando).
        2. En caso de error muestra el mensaje en form_status de la vista.
        3. Si todo va bien: resetea formulario, recarga tabla y avisa al controlador cliente
           para que invalide su caché de carta (así el cliente verá los cambios).
        """
        if self._admin_productos_widget is None:
            return
        try:
            self.guardar_producto(nombre, precio, ingredientes, disponible, stock, categoria)
        except Exception as exc:
            self._admin_productos_widget.form_status.setText(str(exc))
            return
        self._admin_productos_widget.activar_modo_creacion()
        self._cargar_admin_productos_en_vista(self._admin_productos_widget)
        # ⚠️ Punto clave: invalidar_carta() notifica al lado del cliente que la carta cambió
        self._vista.get_ctrl_cliente().invalidar_carta()

    def _on_confirmar_eliminar_producto(self, nombre_producto):
        """
        Señal: el usuario pulsó 'Eliminar' en la tabla de productos.
        Muestra un diálogo de confirmación antes de ejecutar el borrado.
        """
        if self._vista.pedir_confirmacion("Eliminar producto", f"¿Quieres eliminar {nombre_producto}?"):
            self._on_eliminar_producto(nombre_producto)

    def _on_eliminar_producto(self, nombre_producto):
        """
        Ejecuta el borrado real del producto (solo si se confirmó).
        Tras borrar: resetea formulario, recarga tabla y notifica al controlador cliente.
        """
        if self._admin_productos_widget is None:
            return
        try:
            self.eliminar_producto(nombre_producto)
        except Exception as exc:
            self._admin_productos_widget.mostrar_error_formulario(str(exc))
            return
        self._admin_productos_widget.activar_modo_creacion()
        self._cargar_admin_productos_en_vista(self._admin_productos_widget)
        self._vista.get_ctrl_cliente().invalidar_carta()

    def _on_guardar_promocion(self, datos):
        """
        Señal: el usuario pulsó 'Guardar promoción'.
        Crea la promoción, limpia el formulario de promoción y recarga la tabla.
        Los errores se muestran en promotion_status de la vista.
        """
        if self._admin_productos_widget is None:
            return
        try:
            self.guardar_promocion(datos)
        except Exception as exc:
            self._admin_productos_widget.promotion_status.setText(str(exc))
            return
        self._admin_productos_widget._clear_promotion_form()
        self._cargar_admin_productos_en_vista(self._admin_productos_widget)

    def _on_eliminar_promocion(self, id_promocion):
        """
        Señal: el usuario pulsó 'Eliminar' en la tabla de promociones.
        Pide confirmación y, si se acepta, elimina y recarga la tabla.
        """
        if self._vista.pedir_confirmacion("Eliminar promoción", f"¿Quieres eliminar la promoción {id_promocion}?"):
            try:
                self.eliminar_promocion(id_promocion)
            except Exception as exc:
                if self._admin_productos_widget:
                    self._admin_productos_widget.promotion_status.setText(str(exc))
                return
            self._cargar_admin_productos_en_vista(self._admin_productos_widget)

    def _cargar_admin_productos_en_vista(self, vista):
        """
        Recarga TODOS los datos de la pantalla de productos:
          1. Schema → si la BD tiene columna de categoría activa el selector en el formulario.
          2. Categorías → popula el ComboBox de categorías.
          3. Productos → llena la tabla; si está vacía muestra mensaje orientativo.
          4. Promociones → convierte VOs a formato vista y llena la tabla de promociones.
        Cada bloque tiene su propio try/except para que un fallo parcial no rompa el resto.
        """
        if vista is None:
            return
        # 1. Configurar schema (¿tiene columna categoría?)
        try:
            schema = self.obtener_schema_productos()
            tiene_categoria = bool(schema.get("category_column"))
            vista.configurar_schema(
                tiene_categoria,
                "Selecciona una categoria valida de la carta." if tiene_categoria
                else "La BD actual no tiene columna de categorias en PRODUCTOS.",
            )
        except Exception as exc:
            vista.configurar_schema(False, str(exc))
        # 2. Categorías para el formulario
        try:
            vista.inicializar_categorias(self.obtener_categorias())
        except Exception:
            vista.inicializar_categorias([])
        # 3. Tabla de productos
        try:
            productos = self.listar_productos()
            mensaje = "Puedes crear el primer producto desde el formulario." if not productos else ""
            vista.set_productos(productos, mensaje)
        except Exception as exc:
            vista.mostrar_error_productos(str(exc))
        # 4. Tabla de promociones
        try:
            promociones = self.listar_promociones()
            promociones_vista = self.preparar_promociones_vista(promociones)
            mensaje = "Puedes crear la primera promocion desde este bloque." if not promociones_vista else ""
            vista.set_promociones(promociones_vista, mensaje)
        except Exception as exc:
            vista.mostrar_error_promociones(str(exc))

    # ── Manejadores internos — señales de la vista de PERSONAL ────────────────

    def _on_editar_empleado(self, empleado):
        """
        Señal: el usuario pulsó 'Editar' en la tabla de empleados.
        Guarda el empleado en edición en el sub-controlador y activa el modo edición en la vista.
        """
        self.iniciar_edicion_empleado(empleado)
        if self._admin_personal_widget is not None:
            self._admin_personal_widget.activar_modo_edicion(empleado)

    def _on_guardar_empleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        """
        Señal: el usuario pulsó 'Guardar' en el formulario de empleado.
        Si id_empleado llega como None, intenta recuperarlo desde el sub-controlador
        (puede ocurrir si la vista no lo propaga correctamente).
        Crea o actualiza según corresponda, limpia edición y recarga tabla.
        """
        try:
            if id_empleado is None:
                # Fallback: leer el id guardado en el sub-controlador
                id_empleado = self._ctrl_empleados._empleado_en_edicion_id
            if id_empleado is None:
                self._ctrl_empleados.crearEmpleado(ssn, usuario, correo, contrasena, tipo)
            else:
                self._ctrl_empleados.actualizarEmpleado(id_empleado, ssn, usuario, correo, contrasena, tipo)
        except Exception as exc:
            if self._admin_personal_widget is not None:
                self._admin_personal_widget.mostrar_error(str(exc))
            return
        self.limpiar_edicion_empleado()
        if self._admin_personal_widget is not None:
            self._admin_personal_widget.activar_modo_creacion()
        self._cargar_personal_en_vista(self._admin_personal_widget)

    def _on_confirmar_eliminar_empleado(self, id_empleado):
        """
        Señal: el usuario pulsó 'Eliminar' en la tabla de empleados.
        Pide confirmación antes de borrar.
        """
        if self._vista.pedir_confirmacion("Eliminar empleado", "¿Quieres eliminar a este empleado?"):
            self._on_eliminar_empleado(id_empleado)

    def _on_eliminar_empleado(self, id_empleado):
        """
        Ejecuta el borrado real del empleado.
        Limpia edición y recarga la tabla si tiene éxito.
        """
        try:
            self.eliminar_empleado(id_empleado)
        except Exception as exc:
            if self._admin_personal_widget is not None:
                self._admin_personal_widget.mostrar_error(str(exc))
            return
        self.limpiar_edicion_empleado()
        if self._admin_personal_widget is not None:
            self._admin_personal_widget.activar_modo_creacion()
        self._cargar_personal_en_vista(self._admin_personal_widget)

    def _cargar_personal_en_vista(self, vista_personal):
        """
        Recarga la tabla de empleados.
        Si no hay empleados, muestra un mensaje orientativo en la vista.
        """
        if vista_personal is None:
            return
        try:
            empleados = self.listar_empleados()
            vista_personal.set_empleados(empleados)
            if not empleados:
                vista_personal.mostrar_info("Puedes crear el primer empleado desde el formulario.")
        except Exception as exc:
            vista_personal.mostrar_error(str(exc))

    def _confirmar_cerrar_sesion(self):
        """
        Señal común de dashboard y personal: 'Cerrar sesión'.
        Pide confirmación y, si se acepta, vuelve a la pantalla de login.
        """
        if self._vista.pedir_confirmacion("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
            self._vista.mostrar_login()

    # ── Limpieza interna ──────────────────────────────────────────────────────

    def _close_admin_children(self):
        """
        Cierra y desreferencia las sub-vistas de productos y personal.
        Se llama siempre antes de mostrar una nueva sub-vista para no acumular widgets.
        El dashboard no se cierra aquí porque se gestiona por separado.
        """
        for attr in ("_admin_productos_widget", "_admin_personal_widget"):
            widget = getattr(self, attr)
            if widget is not None:
                widget.close()
                setattr(self, attr, None)

    def limpiar_widgets(self):
        """
        Punto de entrada que llama VentanaPrincipal al cerrar sesión.
        Cierra todos los widgets activos del admin y limpia también el dashboard.
        """
        self._close_admin_children()
        self._admin_dashboard_widget = None