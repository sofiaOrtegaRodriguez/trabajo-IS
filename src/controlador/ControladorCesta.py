class ControladorCesta:
    def __init__(self, servicio_cesta):
        self._servicio = servicio_cesta

    def set_cliente(self, cliente):
        self._servicio.set_cliente(cliente)

    def set_session(self, sesion):
        self._servicio.set_session(sesion)

    @property
    def permite_puntos(self):
        return self._servicio.permite_puntos

    @property
    def puntos_disponibles(self):
        return self._servicio.puntos_disponibles

    @property
    def descuento_aplicado(self):
        return self._servicio.descuento_aplicado

    @property
    def puntos_canjeados(self):
        return self._servicio.puntos_canjeados

    @property
    def puntos_usados(self):
        return self._servicio.puntos_usados

    def puede_canjear_puntos(self):
        return self._servicio.puede_canjear_puntos()

    def puede_finalizar_pedido(self):
        return self._servicio.puede_finalizar_pedido()

    def puede_abandonar_pedido(self):
        return self._servicio.puede_abandonar_pedido()

    def add_item(self, product, amount=1):
        self._servicio.add_item(product, amount)

    def remove_item(self, product_id):
        self._servicio.remove_item(product_id)

    def incrementar(self, product_id):
        self._servicio.incrementar(product_id)

    def decrementar(self, product_id):
        self._servicio.decrementar(product_id)

    def eliminar_item(self, product_id):
        self._servicio.eliminar_item(product_id)

    def obtener_items(self):
        return self._servicio.obtener_items()

    def cantidad_producto(self, product_id):
        return self._servicio.cantidad_producto(product_id)

    def calcular_subtotal(self):
        return self._servicio.calcular_subtotal()

    def calcular_total(self):
        return self._servicio.calcular_total()

    def resumen_vista(self):
        return self._servicio.resumen_vista()

    def previsualizar_canje_puntos(self):
        return self._servicio.previsualizar_canje_puntos()

    def canjear_puntos(self):
        self._servicio.canjear_puntos()

    def intentar_canjear_puntos(self):
        return self._servicio.intentar_canjear_puntos()

    def finalizar_pedido(self, total=None):
        return self._servicio.finalizar_pedido(total)

    def intentar_finalizar_pedido(self):
        return self._servicio.intentar_finalizar_pedido()

    def vaciar_cesta(self):
        self._servicio.vaciar_cesta()

    def intentar_abandonar_pedido(self):
        return self._servicio.intentar_abandonar_pedido()

    def snapshot_history(self):
        return self._servicio.snapshot_history()

    def obtener_historial(self):
        return self._servicio.obtener_historial()
