"""
controlador que orquesta toda la interacción del cliente con la app:
carta, cesta e historiaal. coordina la vista principal, el servicio cesta
y las "fábricas" que crean cada widget de vista cuando se necesita
"""

class ControladorCliente:
    def __init__(self, ref_modelo, ref_vista_principal, ref_servicio_cesta, ref_ctrl_productos):
        self._modelo = ref_modelo # referencia al modelo (capa de lógica de negocio)
        self._vista = ref_vista_principal # referencia a la ventana principal (VentanaPrincipal)
        self._cesta = ref_servicio_cesta # servicio de cesta (gestiona items, puntos, pedidos)
        self._ctrl_productos = ref_ctrl_productos # controlador de productos para consultat el catálogo
        self._catalogo_por_id = {} # diccionario {id_producto:producto} para añadir a cesta rápido
        self._flujo_carta = self._modelo.crear_servicio_flujo_carta(self._cesta) # servicio que gestiona paginación de la carta
        self._carta_widget = None # ref. al widget de carta actualmente mostrado
        self._cesta_widget = None # ref. al widget de cesta actualmente mostrado
        self._historial_widget = None # ref. al widget de historial actualmente mostrado


        # las fábricas son funciones que crean instancias nuevas de cada vista (patrón Factory)
        # se inyectan después con set_fabricas_vistas para no acoplar este controlador a las clases UI concretas
        self._fabrica_carta = None
        self._fabrica_cesta = None
        self._fabrica_historial = None

    # inyecta las funciones fábrica que crean cada vista; se llama una vez al iniciar la app
    def set_fabricas_vistas(self, fabrica_carta, fabrica_cesta, fabrica_historial):
        self._fabrica_carta = fabrica_carta
        self._fabrica_cesta = fabrica_cesta
        self._fabrica_historial = fabrica_historial


    # navega a la pantalla de la carta: carga los productos de la página actual,
    # crea el widget con la fábrica, conecta todas sus señales y lo muestra
    def ir_carta(self):
        try:
            render = self._flujo_carta.cargar_pagina_actual() # pide al servicio los datos de la página actual
        except Exception as exc:
            self._vista.mostrar_error("Error al cargar la carta", str(exc)) 
            self._vista.mostrar_login() # si falla la carga, devolvemos al usuario al login
            return

        nueva_carta = self._fabrica_carta() # creamos una nueva instancia de la vista carta
        self._catalogo_por_id = render["catalogo_por_id"] # guardamos el catálogo para usarlo al añadir productos
        nueva_carta.mostrar_productos(render["productos_render"])
        nueva_carta.set_page_info(render["info_pagina"])
        nueva_carta.set_categoria_activa(self._flujo_carta.categoria_actual)


        # conectamos todas las señales de la vista carta con los métodos de este controlador
        nueva_carta.category_clicked.connect(self._on_cambiar_categoria_carta)
        nueva_carta.next_clicked.connect(self._on_siguiente_pagina_carta)
        nueva_carta.prev_clicked.connect(self._on_anterior_pagina_carta)
        nueva_carta.add_product.connect(self._on_agregar_a_cesta)
        nueva_carta.remove_product.connect(self._on_quitar_de_cesta)
        nueva_carta.cart_clicked.connect(self.ir_cesta)
        nueva_carta.profile_clicked.connect(self.ir_historial)

        # según el rol de la sesión, el botón de la carta dice "Volver" (cajero) o "Cerrar Sesión" (cliente) 
        sesion = self._vista.get_sesion_actual()
        es_cajero = bool(sesion and getattr(sesion, "es_cajero", False))
        nueva_carta.set_texto_sesion("Volver" if es_cajero else "Cerrar Sesión")
        nueva_carta.cerrar_sesion.connect(self._cerrar_sesion_desde_carta)


        self._carta_widget = nueva_carta # guardamos la referencia para poder actualizarla después
        self._vista.mostrar_widget(nueva_carta) # le decimos a la ventana principal que muestre este widget
        self._vista.showMaximized() # maximizamos ventana

    # navega de la pantalla a la cesta: obtiene el estado actual de la cesta,
    # crea el widget con la fábrica y conecta sus señales
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
        self._sincronizar_cesta_vista() # nos asegura que la vista muestre los datos más actuales

    # navega a la pantalla del historial: obtiene los pedidos pasados del cliente
    # y crea el widget con la fábrica
    def ir_historial(self):
        pedidos = self.obtener_historial()
        sesion = self._vista.get_sesion_actual()
        nuevo_historial = self._fabrica_historial(cliente=sesion, pedidos=pedidos)
        nuevo_historial.volver_menu.connect(self.ir_carta)
        nuevo_historial.cerrar_sesion.connect(self._confirmar_cerrar_sesion)
        self._historial_widget = nuevo_historial
        self._vista.mostrar_widget(nuevo_historial)

    # agrega un producto a la cesta buscándolo en el catálogo cargado por id
    def agregar_a_cesta(self, product_id, amount):
        product = self._catalogo_por_id.get(product_id)
        if product is None: # si es producto no existe, no hacemos nada
            return
        self._cesta.add_item(product, amount)

    # quita una unidad de un producto de la cesta (decrementa)
    def quitar_de_cesta(self, product_id):
        self._cesta.remove_item(product_id)

    # elimina por completo un producto de la cesta, sin importar la cant.
    def eliminar_item_cesta(self, product_id):
        self._cesta.eliminar_item(product_id)

    # devuelve el estado actual de la cesta: items y resumen (totales, puntos, etc.)
    def obtener_estado_cesta(self):
        return {"items": self._cesta.obtener_items(), "resumen": self._cesta.resumen_vista()}

    # devuelve un diccionario {id_producto:cant.} para sincronizar las tarjetaas de la carta
    def obtener_cantidades_cesta(self):
        return {item["id"]: item["cantidad"] for item in self._cesta.obtener_items()}

    # devuelve una previsualización de cuántos puntos se usarían y qué descuento daría
    def previsualizacion_canje_puntos(self):
        return self._cesta.previsualizar_canje_puntos()

    # comprueba si el usuario puede canjear puntos en ese momento
    def puede_canjear_puntos(self):
        return self._cesta.puede_canjear_puntos()

    # intenta canjear los ptos. disponibles, deleganfo la lógica al servicio de cesta
    def intentar_canjear_puntos(self):
        return self._cesta.intentar_canjear_puntos()

    # intenta finalizar el pedido actual, delegando la lóogica al servicio de cesta
    def intentar_finalizar_pedido(self):
        return self._cesta.intentar_finalizar_pedido()

    # intenta abandonar (vaciar) el pedido actual, delegando la lógica al servicio de cesta
    def intentar_abandonar_pedido(self):
        return self._cesta.intentar_abandonar_pedido()
 
    # devuelve el historial de pedidos pasados del cliente
    def obtener_historial(self):
        return self._cesta.obtener_historial()
     
    # limpia las referencias a los widgets actuales (ejemplo uso: cerrar sesión)
    def limpiar_widgets(self):
        self._carta_widget = None
        self._cesta_widget = None
        self._historial_widget = None

    # invalida el caché de la carta para forzar que se recarguen los productos desde la BD
    # útil cuando un admin modifica el menú y hay que reflejar los cambios
    def invalidar_carta(self):
        """Fuerza que la próxima visita a la carta recargue desde BD."""
        self._carta_widget = None
        self._flujo_carta = self._modelo.crear_servicio_flujo_carta(self._cesta) # recreamos el servicio de flujo


    # MANEJADORES DE SEÑALES DE LA CARTA !!!!

    # al pulsar '+' en una tarjera: ñadimos el producto a la cesta y sincronizamos la vista
    def _on_agregar_a_cesta(self, product_id, amount):
        self.agregar_a_cesta(product_id, amount)
        self._sincronizar_cesta_vista()

    # al pulsar '-' en una tarjera: quitamos una unidad el producto de la cesta y sincronizamos la vista
    def _on_quitar_de_cesta(self, product_id):
        self.quitar_de_cesta(product_id)
        self._sincronizar_cesta_vista()

    # al pulsar una categoría distinta: pedimos al flujo de la carta que cambie de categoría
    # y actualizamos el widdget con los nuevos productos
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

    # al pulsar el botón de siguiente página
    def _on_siguiente_pagina_carta(self):
        try:
            self._mover_pagina_carta(1)
        except Exception as exc:
            self._vista.mostrar_aviso("Carta", str(exc))

    # al pulsar el botón de página anterior
    def _on_anterior_pagina_carta(self):
        try:
            self._mover_pagina_carta(-1)
        except Exception as exc:
            self._vista.mostrar_aviso("Carta", str(exc))


# MANEJADORES DE SEÑALES DE LA CESTA !!!!!!!!!!!!!

    # al confirmar eliminar un producto de la cesta: lo eliminamos y sincronizamos la vista
    def _on_eliminar_item_cesta(self, product_id):
        self.eliminar_item_cesta(product_id)
        self._sincronizar_cesta_vista()

    # gestiona el flujo completo de canjear puntos: comprueba si se puede, pide confirmación
    # con la previsualización del descuento, y si el user aceepta, ejecuta el canje real
    def _on_canjear_puntos(self):
        if not self.puede_canjear_puntos():
            # si no se puede canjear, intentamos igualmente para obtener mensaje de error explicativo
            ok, mensaje = self.intentar_canjear_puntos()
            if self._cesta_widget is not None:
                self._cesta_widget.mostrar_mensaje("Puntos", mensaje)
            return
        puntos, descuento = self.previsualizacion_canje_puntos() # calculamos cuánto se canjearía
        if not self._vista.mostrar_dialogo_canje(puntos, descuento): # pedimos confirmación al user
            return # si user cancela, no hacemos más
        ok, mensaje = self.intentar_canjear_puntos() # ejecutamoss canje real
        if not ok:
            if self._cesta_widget is not None:
                self._cesta_widget.mostrar_mensaje("Puntos", mensaje)
            return
        self._sincronizar_cesta_vista() # actualizamos vista con el nuevo descuento aplicado

    # gestiona el flujo de finalizar el pedido: intenta finalizarlo y muestra el resultado
    def _on_finalizar_pedido(self):
        ok, resultado = self.intentar_finalizar_pedido()
        if not ok:
            if self._cesta_widget:
                self._cesta_widget.mostrar_mensaje("Pedido", resultado) # si falla mostramos motivo
            return
        codigo, puntos, total = resultado # si tiene éxito, desempaquetamaos resultado
        self._vista.mostrar_fin_pedido(codigo, total, puntos) # mostramos el diálogo de pedido confirmado

    #  gestiona flujo de abandonar pedido actual
    def _on_abandonar_pedido(self):
        ok, mensaje = self.intentar_abandonar_pedido()
        if not ok:
            if self._cesta_widget is not None:
                self._cesta_widget.mostrar_mensaje("Cesta vacia", mensaje)
            return
        self._sincronizar_cesta_vista()

# mantiene sincronizados los widgets de cesta y carta tras cualquier cambio en la cesta:
# actualiza el resumen en la vista de cesta y las cant. mostradas en tarjetas de la carta
    def _sincronizar_cesta_vista(self):
        estado = self.obtener_estado_cesta()
        sesion = self._vista.get_sesion_actual()
        if self._cesta_widget is not None:
            self._cesta_widget.set_estado(items=estado["items"], resumen=estado["resumen"], cliente=sesion)
        if self._carta_widget is not None:
            cantidades = self.obtener_cantidades_cesta()
            for pid, qty in cantidades.items():
                self._carta_widget.set_cantidad_producto(pid, qty) # actu. cada tarjeta con su cant. actual

    # decide qué hacer al pulsar 'volveer/cerrar sesión' desde la carta:
    # si es cajero, vuelce al panel de pedidos, si es cliente, pide confirmación para cerrar sesión
    def _cerrar_sesion_desde_carta(self):
        sesion = self._vista.get_sesion_actual()
        es_cajero = bool(sesion and getattr(sesion, "es_cajero", False))
        if es_cajero:
            self._vista.ir_panel_pedidos()
        else:
            self._confirmar_cerrar_sesion()

    # pide confirmación antes de cerrar, y si user confirma, vuelve el login.
    def _confirmar_cerrar_sesion(self):
        if self._vista.pedir_confirmacion("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
            self._vista.mostrar_login()

    # función auxiliar que mueve la página de la carta (delta = 1 siguiente, -1 anterior)
    # y refresca el widget con los nuevos productos de esa página
    def _mover_pagina_carta(self, delta):
        render = self._flujo_carta.mover_pagina(delta)
        self._catalogo_por_id = render["catalogo_por_id"]
        self._carta_widget.mostrar_productos(render["productos_render"])
        self._carta_widget.set_categoria_activa(self._flujo_carta.categoria_actual)
        self._carta_widget.set_page_info(render["info_pagina"])
