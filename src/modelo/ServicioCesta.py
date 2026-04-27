from src.modelo.dao.PedidoDaoSQLServer import PedidoDaoSQLServer
from src.modelo.dao.UserDaoSQLServer import UserDaoSQLServer


class ServicioCesta:
    def __init__(self):
        self._items = {}
        self._sesion = None
        self._descuento_aplicado = 0.0
        self._puntos_canjeados = False
        self._puntos_usados = 0

    def set_cliente(self, cliente):
        self.set_session(cliente)

    def set_session(self, sesion):
        self._sesion = sesion
        self._descuento_aplicado = 0.0
        self._puntos_canjeados = False
        self._puntos_usados = 0

    @property
    def permite_puntos(self):
        return bool(self._sesion is not None and getattr(self._sesion, "permite_puntos", True))

    @property
    def puntos_disponibles(self):
        if not self.permite_puntos:
            return 0
        return int(getattr(self._sesion, "puntos", 0) or 0)

    @property
    def descuento_aplicado(self):
        return round(self._descuento_aplicado, 2)

    @property
    def puntos_canjeados(self):
        return self._puntos_canjeados

    def add_item(self, product, amount=1):
        product_id = product["id"]
        current = self._items.get(product_id)
        if current is None:
            current = {
                "id": product_id,
                "nombre": product["nombre"],
                "precio": float(product["precio"]),
                "cantidad": 0,
            }
            self._items[product_id] = current
        current["cantidad"] += max(1, int(amount))

    def remove_item(self, product_id):
        self.decrementar(product_id)

    def incrementar(self, nombre):
        item = self._items.get(nombre)
        if item is None:
            return
        item["cantidad"] += 1

    def decrementar(self, nombre):
        item = self._items.get(nombre)
        if item is None:
            return
        item["cantidad"] = max(0, item["cantidad"] - 1)
        if item["cantidad"] == 0:
            self._items.pop(nombre, None)

    def eliminar_item(self, nombre):
        self._items.pop(nombre, None)

    def obtener_items(self):
        return list(self._items.values())

    def cantidad_producto(self, product_id):
        item = self._items.get(product_id)
        if item is None:
            return 0
        return int(item.get("cantidad", 0) or 0)

    def calcular_subtotal(self):
        return round(
            sum(item["precio"] * item["cantidad"] for item in self._items.values()),
            2,
        )

    def calcular_total(self):
        total = self.calcular_subtotal() - self._descuento_aplicado
        return round(max(0.0, total), 2)

    def canjear_puntos(self):
        if not self.permite_puntos or self._puntos_canjeados or not self._items:
            return
        subtotal = self.calcular_subtotal()
        descuento = min(self.puntos_disponibles / 100.0, subtotal)
        self._descuento_aplicado = round(descuento, 2)
        self._puntos_canjeados = True
        self._puntos_usados = self.puntos_disponibles
        if hasattr(self._sesion, "consumir_puntos"):
            self._sesion.consumir_puntos(self.puntos_disponibles)

    def finalizar_pedido(self):
        if not self._items:
            raise ValueError("No hay productos en la cesta.")
        if self._sesion is None:
            raise ValueError("No hay una sesión activa.")

        total = self.calcular_total()
        pedido_dao = PedidoDaoSQLServer()
        pedido_id = pedido_dao.crear(self._sesion, self.obtener_items(), total)

        puntos_ganados = 0
        if self.permite_puntos:
            if self._puntos_usados:
                UserDaoSQLServer().actualizarPuntos(self._sesion.id_sesion, -self._puntos_usados)
            puntos_ganados = int(round(total * 10))
            if puntos_ganados > 0:
                UserDaoSQLServer().actualizarPuntos(self._sesion.id_sesion, puntos_ganados)
                if hasattr(self._sesion, "sumar_puntos"):
                    self._sesion.sumar_puntos(puntos_ganados)

        self.vaciar_cesta()
        return pedido_id, puntos_ganados

    def vaciar_cesta(self):
        self._items.clear()
        self._descuento_aplicado = 0.0
        self._puntos_canjeados = False
        self._puntos_usados = 0

    def snapshot_history(self):
        if self._sesion is None:
            return []
        return PedidoDaoSQLServer().listar(self._sesion)

    def obtener_historial(self):
        return self.snapshot_history()
