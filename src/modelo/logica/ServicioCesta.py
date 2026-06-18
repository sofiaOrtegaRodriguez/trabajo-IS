from src.modelo.dao.PedidoDaoJDBC import PedidoDaoJDBC
from src.modelo.dao.UserDaoJDBC import UserDaoJDBC


class ServicioCesta:
    def __init__(self, pedido_dao, user_dao):
        if pedido_dao is None or user_dao is None:
            raise ValueError("ServicioCesta requiere pedido_dao y user_dao inyectados.")
        self._items = {}
        self._sesion = None
        self._descuento_aplicado = 0.0
        self._puntos_canjeados = False
        self._puntos_usados = 0
        self._pedido_dao = pedido_dao
        self._user_dao = user_dao

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

    @property
    def puntos_usados(self):
        return int(self._puntos_usados)

    def add_item(self, product, amount=1):
        product_id = product["id"]
        current = self._items.get(product_id)
        if current is None:
            current = {
                "id": product_id,
                "nombre": product["nombre"],
                "precio": float(product["precio"]),
                "stock": int(product.get("stock", 999)),
                "cantidad": 0,
            }
            self._items[product_id] = current
        current["cantidad"] += max(1, int(amount))

    def remove_item(self, product_id):
        self.decrementar(product_id)

    def incrementar(self, product_id):
        item = self._items.get(product_id)
        if item is None:
            return
        stock = int(item.get("stock", 999))
        if item["cantidad"] >= stock:
            return
        item["cantidad"] += 1

    def decrementar(self, product_id):
        item = self._items.get(product_id)
        if item is None:
            return
        item["cantidad"] = max(0, item["cantidad"] - 1)
        if item["cantidad"] == 0:
            self._items.pop(product_id, None)

    def eliminar_item(self, product_id):
        self._items.pop(product_id, None)

    def obtener_items(self):
        return list(self._items.values())

    def cantidad_producto(self, product_id):
        item = self._items.get(product_id)
        if item is None:
            return 0
        return int(item.get("cantidad", 0) or 0)

    def calcular_subtotal(self):
        return round(sum(item["precio"] * item["cantidad"] for item in self._items.values()), 2)

    def calcular_total(self):
        total = self.calcular_subtotal() - self._descuento_aplicado
        return round(max(0.0, total), 2)

    def tiene_items(self):
        return bool(self._items)

    def puede_canjear_puntos(self):
        return self.permite_puntos and not self._puntos_canjeados and self.tiene_items() and self.puntos_disponibles > 0

    def puede_finalizar_pedido(self):
        return self.tiene_items() and self._sesion is not None

    def puede_abandonar_pedido(self):
        return self.tiene_items()

    def resumen_vista(self):
        puntos = self.puntos_disponibles
        tiene_descuento = self.permite_puntos and self._puntos_canjeados and self._descuento_aplicado > 0
        boton_canjear_habilitado = self.puede_canjear_puntos()
        if not self.permite_puntos:
            boton_canjear_texto = "Puntos desactivados"
        elif self._puntos_canjeados:
            boton_canjear_texto = "Puntos canjeados"
        else:
            boton_canjear_texto = "Canjear puntos"
        return {
            "total": self.calcular_total(),
            "puntos": puntos,
            "descuento": self.descuento_aplicado if tiene_descuento else 0.0,
            "header": f"{puntos} pts" if self.permite_puntos else "Cajero",
            "mostrar_descuento": tiene_descuento,
            "boton_canjear_texto": boton_canjear_texto,
            "boton_canjear_habilitado": boton_canjear_habilitado,
        }

    def previsualizar_canje_puntos(self):
        if not self.puede_canjear_puntos():
            return 0, 0.0
        subtotal = self.calcular_subtotal()
        descuento = min(self.puntos_disponibles / 100.0, subtotal)
        puntos_necesarios = int(round(descuento * 100))
        return puntos_necesarios, round(puntos_necesarios / 100.0, 2)

    def canjear_puntos(self):
        if not self.puede_canjear_puntos():
            return
        puntos_necesarios, descuento = self.previsualizar_canje_puntos()
        self._descuento_aplicado = descuento
        self._puntos_canjeados = True
        self._puntos_usados = min(self.puntos_disponibles, puntos_necesarios)

    def intentar_canjear_puntos(self):
        if not self.tiene_items():
            return False, "Añade productos primero."
        if not self.permite_puntos:
            return False, "Puntos desactivados."
        if self._puntos_canjeados:
            return False, "Los puntos ya se han canjeado en este pedido."
        if self.puntos_disponibles == 0:
            return False, "No tienes puntos disponibles."
        self.canjear_puntos()
        return True, None

    def finalizar_pedido(self, total=None):
        if not self.tiene_items():
            raise ValueError("No hay productos en la cesta.")
        if self._sesion is None:
            raise ValueError("No hay una sesion activa.")
        total_final = self.calcular_total() if total is None else float(total)
        pedido_id = self._pedido_dao.crear(self._sesion, self.obtener_items(), total_final)
        puntos_ganados = 0
        if self.permite_puntos:
            if self._puntos_usados:
                self._user_dao.actualizarPuntos(self._sesion.id_sesion, -self._puntos_usados)
                if hasattr(self._sesion, "consumir_puntos"):
                    self._sesion.consumir_puntos(self._puntos_usados)
            puntos_ganados = int(round(total_final * 10))
            if puntos_ganados > 0:
                self._user_dao.actualizarPuntos(self._sesion.id_sesion, puntos_ganados)
                if hasattr(self._sesion, "sumar_puntos"):
                    self._sesion.sumar_puntos(puntos_ganados)
        self.vaciar_cesta()
        return pedido_id, puntos_ganados

    def intentar_finalizar_pedido(self):
        if not self.tiene_items():
            return False, "Añade productos antes de finalizar."
        if self._sesion is None:
            return False, "No hay una sesion activa."
        total = self.calcular_total()
        pedido_id, puntos_ganados = self.finalizar_pedido(total)
        return True, (pedido_id, puntos_ganados, total)

    def intentar_abandonar_pedido(self):
        if not self.tiene_items():
            return False, "No hay productos en la cesta."
        self.vaciar_cesta()
        return True, None

    def vaciar_cesta(self):
        self._items.clear()
        self._descuento_aplicado = 0.0
        self._puntos_canjeados = False
        self._puntos_usados = 0

    def snapshot_history(self):
        if self._sesion is None:
            return []
        return self._pedido_dao.listar(self._sesion)

    def obtener_historial(self):
        return self.snapshot_history()
