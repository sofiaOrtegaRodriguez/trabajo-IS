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
        self._modelo = ref_modelo
        self._vista = ref_vista_principal
        self._ctrl_productos = ref_controlador_productos
        self._ctrl_empleados = ref_controlador_empleados
        self._producto_editando = None

        # Referencias a sub-vistas activas
        self._admin_dashboard_widget = None
        self._admin_productos_widget = None
        self._admin_personal_widget = None

        # Fábricas de vistas — se inyectan desde VentanaPrincipal  ← AÑADIR ESTO
        self._fabrica_dashboard = None
        self._fabrica_productos = None
        self._fabrica_personal = None

    # ── Inyección de fábricas de vistas ──────────────────────────────────────  ← AÑADIR ESTO
    def set_fabricas_vistas(self, fabrica_dashboard, fabrica_productos, fabrica_personal):
        self._fabrica_dashboard = fabrica_dashboard
        self._fabrica_productos = fabrica_productos
        self._fabrica_personal = fabrica_personal

    # ── Navegación ────────────────────────────────────────────────────────────

    def ir_dashboard(self):
        """Muestra el dashboard del administrador."""
        self._close_admin_children()
        sesion = self._vista.get_sesion_actual()
        dashboard = self._fabrica_dashboard(sesion)
        dashboard.productos_clicked.connect(self.ir_productos)
        dashboard.personal_clicked.connect(self.ir_personal)
        dashboard.cerrar_sesion.connect(self._confirmar_cerrar_sesion)
        self._admin_dashboard_widget = dashboard
        self._vista.mostrar_widget(dashboard)

    def ir_productos(self):
        """Muestra la pantalla de gestión de productos."""
        self._close_admin_children()
        ventana = self._fabrica_productos()
        ventana.volver_menu.connect(self.ir_dashboard)
        ventana.editar_producto_requested.connect(self._on_editar_producto)
        ventana.guardar_producto_requested.connect(self._on_guardar_producto)
        ventana.eliminar_producto_requested.connect(self._on_confirmar_eliminar_producto)
        ventana.guardar_promocion_requested.connect(self._on_guardar_promocion)
        ventana.eliminar_promocion_requested.connect(self._on_eliminar_promocion)
        self._admin_productos_widget = ventana
        ventana.activar_modo_creacion()
        self._cargar_admin_productos_en_vista(ventana)
        self._vista.mostrar_widget(ventana)
        self._vista.adjustSize()

    def ir_personal(self):
        """Muestra la pantalla de gestión de personal."""
        self._close_admin_children()
        sesion = self._vista.get_sesion_actual()
        ventana = self._fabrica_personal(sesion)
        ventana.volver_menu.connect(self.ir_dashboard)
        ventana.editar_empleado_requested.connect(self._on_editar_empleado)
        ventana.guardar_empleado_requested.connect(self._on_guardar_empleado)
        ventana.eliminar_empleado_requested.connect(self._on_confirmar_eliminar_empleado)
        ventana.cerrar_sesion.connect(self._confirmar_cerrar_sesion)
        self._cargar_personal_en_vista(ventana)
        ventana.inicializar_tipos(self.obtener_tipos_empleado())
        ventana.activar_modo_creacion()
        self._admin_personal_widget = ventana
        self._vista.mostrar_widget(ventana)
        self._vista.adjustSize()

    # ── Productos ─────────────────────────────────────────────────────────────

    def obtener_schema_productos(self):
        """Devuelve el schema de la tabla PRODUCTOS para configurar la vista."""
        return self._ctrl_productos.describirProductos()

    def obtener_categorias(self):
        """Devuelve la lista de categorías válidas."""
        return self._ctrl_productos.obtenerCategoriasAdmin()

    def listar_productos(self):
        """Devuelve todos los productos como lista de ProductoVo."""
        return self._ctrl_productos.listarProductos()

    def listar_promociones(self):
        """Devuelve todas las promociones."""
        return self._ctrl_productos.listarPromociones()

    def preparar_promociones_vista(self, promociones=None):
        """Prepara las promociones para mostrar en la tabla de la vista."""
        return self._ctrl_productos.prepararPromocionesVista(promociones)

    def iniciar_edicion_producto(self, producto):
        """Guarda el nombre del producto que se va a editar."""
        self._producto_editando = getattr(producto, "nombre", None)

    def limpiar_edicion_producto(self):
        self._producto_editando = None

    def guardar_empleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        if id_empleado is None:
            self._ctrl_empleados.crearEmpleado(ssn, usuario, correo, contrasena, tipo)
        else:
            self._ctrl_empleados.actualizarEmpleado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def guardar_producto(self, nombre, precio, ingredientes, disponible, stock, categoria):
        if self._producto_editando is None:
            self._ctrl_productos.crearProducto(nombre, precio, ingredientes, disponible, stock, categoria)
        else:
            self._ctrl_productos.actualizarProducto(
                self._producto_editando, nombre, precio, ingredientes, disponible, stock, categoria
            )
        self._producto_editando = None

    def eliminar_producto(self, nombre_producto):
        """Elimina un producto y limpia la edición si era el editado."""
        self._ctrl_productos.eliminarProducto(nombre_producto)
        if self._producto_editando == nombre_producto:
            self._producto_editando = None

    def guardar_promocion(self, datos):
        """Crea una nueva promoción."""
        self._ctrl_productos.crearPromocion(
            int(datos.get("descuento", 0)),
            datos.get("fecha_inicio"),
            datos.get("fecha_fin"),
            str(datos.get("nombre_producto", "")).strip(),
        )

    def eliminar_promocion(self, id_promocion):
        """Elimina una promoción."""
        self._ctrl_productos.eliminarPromocion(id_promocion)

    # ── Personal ──────────────────────────────────────────────────────────────

    def listar_empleados(self):
        """Devuelve todos los empleados."""
        return self._ctrl_empleados.listarEmpleados()

    def obtener_tipos_empleado(self):
        """Devuelve los tipos de empleado disponibles."""
        return self._ctrl_empleados.obtenerTiposEmpleado()

    def iniciar_edicion_empleado(self, empleado):
        """Inicia la edición de un empleado."""
        return self._ctrl_empleados.iniciarEdicionEmpleado(empleado)

    def limpiar_edicion_empleado(self):
        """Limpia el estado de edición de empleado."""
        self._ctrl_empleados.limpiarEdicionEmpleado()

    def guardar_empleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        if id_empleado is None:
            self._ctrl_empleados.crearEmpleado(ssn, usuario, correo, contrasena, tipo)
        else:
            self._ctrl_empleados.actualizarEmpleado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def eliminar_empleado(self, id_empleado):
        """Elimina un empleado."""
        self._ctrl_empleados.eliminarEmpleado(id_empleado)

    # ── Manejadores internos de señales — productos ───────────────────────────

    def _on_editar_producto(self, producto):
        self.iniciar_edicion_producto(producto)
        if self._admin_productos_widget is not None:
            self._admin_productos_widget.activar_modo_edicion(producto)

    def _on_guardar_producto(self, nombre, precio, ingredientes, disponible, stock, categoria):
        if self._admin_productos_widget is None:
            return
        try:
            self.guardar_producto(nombre, precio, ingredientes, disponible, stock, categoria)
        except Exception as exc:
            self._admin_productos_widget.form_status.setText(str(exc))
            return
        self._admin_productos_widget.activar_modo_creacion()
        self._cargar_admin_productos_en_vista(self._admin_productos_widget)
        self._vista.get_ctrl_cliente().invalidar_carta()

    def _on_confirmar_eliminar_producto(self, nombre_producto):
        if self._vista.pedir_confirmacion("Eliminar producto", f"¿Quieres eliminar {nombre_producto}?"):
            self._on_eliminar_producto(nombre_producto)

    def _on_eliminar_producto(self, nombre_producto):
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
        if self._vista.pedir_confirmacion("Eliminar promoción", f"¿Quieres eliminar la promoción {id_promocion}?"):
            try:
                self.eliminar_promocion(id_promocion)
            except Exception as exc:
                if self._admin_productos_widget:
                    self._admin_productos_widget.promotion_status.setText(str(exc))
                return
            self._cargar_admin_productos_en_vista(self._admin_productos_widget)
    def _cargar_admin_productos_en_vista(self, vista):
        if vista is None:
            return
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
        try:
            vista.inicializar_categorias(self.obtener_categorias())
        except Exception:
            vista.inicializar_categorias([])
        try:
            productos = self.listar_productos()
            mensaje = "Puedes crear el primer producto desde el formulario." if not productos else ""
            vista.set_productos(productos, mensaje)
        except Exception as exc:
            vista.mostrar_error_productos(str(exc))
        try:
            promociones = self.listar_promociones()
            promociones_vista = self.preparar_promociones_vista(promociones)
            mensaje = "Puedes crear la primera promocion desde este bloque." if not promociones_vista else ""
            vista.set_promociones(promociones_vista, mensaje)
        except Exception as exc:
            vista.mostrar_error_promociones(str(exc))

    # ── Manejadores internos de señales — personal ────────────────────────────

    def _on_editar_empleado(self, empleado):
        self.iniciar_edicion_empleado(empleado)
        if self._admin_personal_widget is not None:
            self._admin_personal_widget.activar_modo_edicion(empleado)

    def _on_guardar_empleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        try:
            if id_empleado is None:
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
        if self._vista.pedir_confirmacion("Eliminar empleado", "¿Quieres eliminar a este empleado?"):
            self._on_eliminar_empleado(id_empleado)

    def _on_eliminar_empleado(self, id_empleado):
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
        if self._vista.pedir_confirmacion("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
            self._vista.mostrar_login()

    # ── Limpieza interna ──────────────────────────────────────────────────────

    def _close_admin_children(self):
        for attr in ("_admin_productos_widget", "_admin_personal_widget"):
            widget = getattr(self, attr)
            if widget is not None:
                widget.close()
                setattr(self, attr, None)

    def limpiar_widgets(self):
        """Llamado por VentanaPrincipal al cerrar sesión."""
        self._close_admin_children()
        self._admin_dashboard_widget = None
