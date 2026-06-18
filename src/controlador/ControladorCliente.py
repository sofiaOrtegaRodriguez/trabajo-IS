class ControladorCliente:
    def __init__(self, ref_modelo, ref_vista_principal, ref_servicio_cesta, ref_ctrl_productos):
        self._modelo = ref_modelo
        self._vista = ref_vista_principal
        self._cesta = ref_servicio_cesta
        self._ctrl_productos = ref_ctrl_productos
        self._catalogo_por_id = {}
        self._flujo_carta = self._modelo.crear_servicio_flujo_carta(self._cesta)
        self._carta_widget = None
        self._cesta_widget = None
        self._historial_widget = None

        self._fabrica_carta = None
        self._fabrica_cesta = None
        self._fabrica_historial = None

    def set_fabricas_vistas(self, fabrica_carta, fabrica_cesta, fabrica_historial):
        self._fabrica_carta = fabrica_carta
        self._fabrica_cesta = fabrica_cesta
        self._fabrica_historial = fabrica_historial

    def ir_carta(self):
        try:
            render = self._flujo_carta.cargar_pagina_actual()
        except Exception as exc:
            self._vista.mostrar_error("Error al cargar la carta", str(exc))
            self._vista.mostrar_login()
            return

        nueva_carta = self._fabrica_carta()
        self._catalogo_por_id = render["catalogo_por_id"]
        nueva_carta.mostrar_productos(render["productos_render"])
        nueva_carta.set_page_info(render["info_pagina"])
        nueva_carta.set_categoria_activa(self._flujo_carta.categoria_actual)
        nueva_carta.category_clicked.connect(self._on_cambiar_categoria_carta)
        nueva_carta.next_clicked.connect(self._on_siguiente_pagina_carta)
        nueva_carta.prev_clicked.connect(self._on_anterior_pagina_carta)
        nueva_carta.add_product.connect(self._on_agregar_a_cesta)
        nueva_carta.remove_product.connect(self._on_quitar_de_cesta)
        nueva_carta.cart_clicked.connect(self.ir_cesta)
        nueva_carta.profile_clicked.connect(self.ir_historial)
        sesion = self._vista.get_sesion_actual()
        es_cajero = bool(sesion and getattr(sesion, "es_cajero", False))
        nueva_carta.set_texto_sesion("Volver" if es_cajero else "Cerrar Sesión")
        nueva_carta.cerrar_sesion.connect(self._cerrar_sesion_desde_carta)
        self._carta_widget = nueva_carta
        self._vista.mostrar_widget(nueva_carta)
        self._vista.showMaximized()

    def ir_cesta(self):
        estado = self.obtener_estado_cesta()
        sesion = self._vista.get_sesion_actual()
        nueva_cesta = self._fabrica_cesta(items=estado["items"], resumen=estado["resumen"], cliente=sesion)
        nueva_cesta.volver_carta.connect(self.ir_carta)
        nueva_cesta.cerrar_sesion.connect(self._vista.mostrar_login)
        nueva_cesta.eliminar_requested.connect(self._on_eliminar_item_cesta)
        nueva_cesta.canjear_requested.connect(self._on_canjear_puntos)
        nueva_cesta.finalizar_requested.connect(self._on_finalizar_pedido)
        nueva_cesta.abandonar_requested.connect(self._on_abandonar_pedido)
        self._cesta_widget = nueva_cesta
        self._vista.mostrar_widget(nueva_cesta)
        self._sincronizar_cesta_vista()

    def ir_historial(self):
        pedidos = self.obtener_historial()
        sesion = self._vista.get_sesion_actual()
        nuevo_historial = self._fabrica_historial(cliente=sesion, pedidos=pedidos)
        nuevo_historial.volver_menu.connect(self.ir_carta)
        nuevo_historial.cerrar_sesion.connect(self._confirmar_cerrar_sesion)
        self._historial_widget = nuevo_historial
        self._vista.mostrar_widget(nuevo_historial)

    def agregar_a_cesta(self, product_id, amount):
        product = self._catalogo_por_id.get(product_id)
        if product is None:
            return
        self._cesta.add_item(product, amount)

    def quitar_de_cesta(self, product_id):
        self._cesta.remove_item(product_id)

    def eliminar_item_cesta(self, product_id):
        self._cesta.eliminar_item(product_id)

    def obtener_estado_cesta(self):
        return {"items": self._cesta.obtener_items(), "resumen": self._cesta.resumen_vista()}

    def obtener_cantidades_cesta(self):
        return {item["id"]: item["cantidad"] for item in self._cesta.obtener_items()}

    def previsualizacion_canje_puntos(self):
        return self._cesta.previsualizar_canje_puntos()

    def puede_canjear_puntos(self):
        return self._cesta.puede_canjear_puntos()

    def intentar_canjear_puntos(self):
        return self._cesta.intentar_canjear_puntos()

    def intentar_finalizar_pedido(self):
        return self._cesta.intentar_finalizar_pedido()

    def intentar_abandonar_pedido(self):
        return self._cesta.intentar_abandonar_pedido()

    def obtener_historial(self):
        return self._cesta.obtener_historial()

    def limpiar_widgets(self):
        self._carta_widget = None
        self._cesta_widget = None
        self._historial_widget = None

    def invalidar_carta(self):
        """Fuerza que la próxima visita a la carta recargue desde BD."""
        self._carta_widget = None
        self._flujo_carta = self._modelo.crear_servicio_flujo_carta(self._cesta)

    def _on_agregar_a_cesta(self, product_id, amount):
        self.agregar_a_cesta(product_id, amount)
        self._sincronizar_cesta_vista()

    def _on_quitar_de_cesta(self, product_id):
        self.quitar_de_cesta(product_id)
        self._sincronizar_cesta_vista()

    def _on_cambiar_categoria_carta(self, categoria):
        try:
            render = self._flujo_carta.cambiar_categoria(categoria)
            self._catalogo_por_id = render["catalogo_por_id"]
            if self._carta_widget is not None:
                self._carta_widget.mostrar_productos(render["productos_render"])
                self._carta_widget.set_categoria_activa(categoria)
                self._carta_widget.set_page_info(render["info_pagina"])
        except Exception as exc:
            self._vista.mostrar_aviso("Carta", str(exc))

    def _on_siguiente_pagina_carta(self):
        try:
            self._mover_pagina_carta(1)
        except Exception as exc:
            self._vista.mostrar_aviso("Carta", str(exc))

    def _on_anterior_pagina_carta(self):
        try:
            self._mover_pagina_carta(-1)
        except Exception as exc:
            self._vista.mostrar_aviso("Carta", str(exc))

    def _on_eliminar_item_cesta(self, product_id):
        self.eliminar_item_cesta(product_id)
        self._sincronizar_cesta_vista()

    def _on_canjear_puntos(self):
        if not self.puede_canjear_puntos():
            ok, mensaje = self.intentar_canjear_puntos()
            if self._cesta_widget is not None:
                self._cesta_widget.mostrar_mensaje("Puntos", mensaje)
            return
        puntos, descuento = self.previsualizacion_canje_puntos()
        if not self._vista.mostrar_dialogo_canje(puntos, descuento):
            return
        ok, mensaje = self.intentar_canjear_puntos()
        if not ok:
            if self._cesta_widget is not None:
                self._cesta_widget.mostrar_mensaje("Puntos", mensaje)
            return
        self._sincronizar_cesta_vista()

    def _on_finalizar_pedido(self):
        ok, resultado = self.intentar_finalizar_pedido()
        if not ok:
            if self._cesta_widget:
                self._cesta_widget.mostrar_mensaje("Pedido", resultado)
            return
        codigo, puntos, total = resultado
        self._vista.mostrar_fin_pedido(codigo, total, puntos)

    def _on_abandonar_pedido(self):
        ok, mensaje = self.intentar_abandonar_pedido()
        if not ok:
            if self._cesta_widget is not None:
                self._cesta_widget.mostrar_mensaje("Cesta vacia", mensaje)
            return
        self._sincronizar_cesta_vista()

    def _sincronizar_cesta_vista(self):
        estado = self.obtener_estado_cesta()
        sesion = self._vista.get_sesion_actual()
        if self._cesta_widget is not None:
            self._cesta_widget.set_estado(items=estado["items"], resumen=estado["resumen"], cliente=sesion)
        if self._carta_widget is not None:
            cantidades = self.obtener_cantidades_cesta()
            for pid, qty in cantidades.items():
                self._carta_widget.set_cantidad_producto(pid, qty)

    def _cerrar_sesion_desde_carta(self):
        sesion = self._vista.get_sesion_actual()
        es_cajero = bool(sesion and getattr(sesion, "es_cajero", False))
        if es_cajero:
            self._vista.ir_panel_pedidos()
        else:
            self._vista.mostrar_login()

    def _confirmar_cerrar_sesion(self):
        if self._vista.pedir_confirmacion("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
            self._vista.mostrar_login()

    def _mover_pagina_carta(self, delta):
        render = self._flujo_carta.mover_pagina(delta)
        self._catalogo_por_id = render["catalogo_por_id"]
        self._carta_widget.mostrar_productos(render["productos_render"])
        self._carta_widget.set_categoria_activa(self._flujo_carta.categoria_actual)
        self._carta_widget.set_page_info(render["info_pagina"])
