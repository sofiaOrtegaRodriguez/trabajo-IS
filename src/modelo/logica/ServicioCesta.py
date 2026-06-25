from src.modelo.dao.PedidoDaoJDBC import PedidoDaoJDBC
from src.modelo.dao.UserDaoJDBC import UserDaoJDBC


# ══════════════════════════════════════════════════════════════
#  ServicioCesta  –  capa de servicio para la cesta de la compra
# ══════════════════════════════════════════════════════════════
class ServicioCesta:
    """
    Gestiona el estado de la cesta durante una sesión de usuario:
      - Añadir / quitar / eliminar productos
      - Cálculo de subtotal, descuentos y total
      - Canje de puntos de fidelización
      - Finalización y abandono del pedido

    Los DAOs se inyectan en el constructor (no se instancian aquí),
    lo que facilita los tests y respeta el patrón Facade.
    """

    def __init__(self, pedido_dao, user_dao):
        if pedido_dao is None or user_dao is None:
            raise ValueError("ServicioCesta requiere pedido_dao y user_dao inyectados.")

        self._items              = {}      # {product_id: {id, nombre, precio, stock, cantidad}}
        self._sesion             = None    # Objeto sesión del cliente activo
        self._descuento_aplicado = 0.0    # Importe descontado por canje de puntos
        self._puntos_canjeados   = False  # Bandera: solo se puede canjear una vez por pedido
        self._puntos_usados      = 0      # Puntos consumidos en el canje actual
        self._pedido_dao         = pedido_dao
        self._user_dao           = user_dao

    # ── Gestión de sesión ─────────────────────────────────────

    def set_cliente(self, cliente):
        """Alias de set_session para compatibilidad con el controlador."""
        self.set_session(cliente)

    def set_session(self, sesion):
        """
        Establece el cliente activo y resetea todo el estado de descuentos/puntos.
        Se llama al iniciar sesión o al cambiar de usuario.
        """
        self._sesion             = sesion
        self._descuento_aplicado = 0.0
        self._puntos_canjeados   = False
        self._puntos_usados      = 0

    # ── Propiedades de puntos y descuentos ────────────────────

    @property
    def permite_puntos(self):
        """True si hay sesión activa y el tipo de cliente tiene puntos habilitados."""
        return bool(self._sesion is not None and getattr(self._sesion, "permite_puntos", True))

    @property
    def puntos_disponibles(self):
        """Puntos actuales del cliente (0 si el sistema de puntos está desactivado)."""
        if not self.permite_puntos:
            return 0
        return int(getattr(self._sesion, "puntos", 0) or 0)

    @property
    def descuento_aplicado(self):
        """Importe del descuento redondeado a 2 decimales."""
        return round(self._descuento_aplicado, 2)

    @property
    def puntos_canjeados(self):
        """True si ya se ha realizado un canje en el pedido actual."""
        return self._puntos_canjeados

    @property
    def puntos_usados(self):
        """Número de puntos consumidos en el canje actual."""
        return int(self._puntos_usados)

    # ── Gestión de ítems ──────────────────────────────────────

    def add_item(self, product, amount=1):
        """
        Añade 'amount' unidades de un producto a la cesta.
        Si el producto ya existe, incrementa su cantidad.
        El dict 'product' debe tener las claves: id, nombre, precio, (stock opcional).
        """
        product_id = product["id"]
        current    = self._items.get(product_id)
        if current is None:
            # Primera vez que se añade este producto: crea la entrada
            current = {
                "id":       product_id,
                "nombre":   product["nombre"],
                "precio":   float(product["precio"]),
                "stock":    int(product.get("stock", 999)),  # 999 = sin límite conocido
                "cantidad": 0,
            }
            self._items[product_id] = current
        current["cantidad"] += max(1, int(amount))

    def remove_item(self, product_id):
        """Alias de decrementar (quita 1 unidad; si llega a 0, elimina el ítem)."""
        self.decrementar(product_id)

    def incrementar(self, product_id):
        """
        Suma 1 unidad a un producto existente.
        No hace nada si el producto no está en la cesta o si se ha alcanzado el stock.
        """
        item = self._items.get(product_id)
        if item is None:
            return
        stock = int(item.get("stock", 999))
        if item["cantidad"] >= stock:
            return   # Límite de stock alcanzado
        item["cantidad"] += 1

    def decrementar(self, product_id):
        """
        Resta 1 unidad. Si la cantidad resultante es 0, elimina el ítem de la cesta.
        Nunca deja cantidades negativas.
        """
        item = self._items.get(product_id)
        if item is None:
            return
        item["cantidad"] = max(0, item["cantidad"] - 1)
        if item["cantidad"] == 0:
            self._items.pop(product_id, None)

    def eliminar_item(self, product_id):
        """Elimina completamente un producto de la cesta, independientemente de su cantidad."""
        self._items.pop(product_id, None)

    def obtener_items(self):
        """Devuelve una copia de la lista de ítems (para que la vista no mute el estado)."""
        return list(self._items.values())

    def cantidad_producto(self, product_id):
        """
        Devuelve la cantidad de un producto concreto en la cesta.
        Usado por CartaUI para inicializar los contadores de cada ProductCard.
        """
        item = self._items.get(product_id)
        if item is None:
            return 0
        return int(item.get("cantidad", 0) or 0)

    # ── Cálculos de precio ────────────────────────────────────

    def calcular_subtotal(self):
        """Suma precio × cantidad para todos los ítems, sin descuentos."""
        return round(sum(item["precio"] * item["cantidad"] for item in self._items.values()), 2)

    def calcular_total(self):
        """
        Total final = subtotal - descuento por puntos.
        Nunca puede ser negativo (mínimo 0.0 €).
        """
        total = self.calcular_subtotal() - self._descuento_aplicado
        return round(max(0.0, total), 2)

    # ── Predicados de estado ──────────────────────────────────

    def tiene_items(self):
        """True si la cesta tiene al menos un producto."""
        return bool(self._items)

    def puede_canjear_puntos(self):
        """True si se cumplen todas las condiciones para canjear puntos."""
        return (
            self.permite_puntos
            and not self._puntos_canjeados      # Solo un canje por pedido
            and self.tiene_items()
            and self.puntos_disponibles > 0
        )

    def puede_finalizar_pedido(self):
        """True si hay ítems y hay sesión activa (requisitos mínimos para pagar)."""
        return self.tiene_items() and self._sesion is not None

    def puede_abandonar_pedido(self):
        """True si hay algo en la cesta que abandonar."""
        return self.tiene_items()

    # ── Datos para la vista ───────────────────────────────────

    def resumen_vista(self):
        """
        Devuelve un dict con todos los datos que necesita CestaUI para renderizarse.
        El controlador llama a este método y pasa el resultado a la vista.

        Claves devueltas:
          total, puntos, descuento, header,
          mostrar_descuento, boton_canjear_texto, boton_canjear_habilitado
        """
        puntos          = self.puntos_disponibles
        tiene_descuento = self.permite_puntos and self._puntos_canjeados and self._descuento_aplicado > 0

        boton_canjear_habilitado = self.puede_canjear_puntos()

        # Texto del botón según el estado del canje
        if not self.permite_puntos:
            boton_canjear_texto = "Puntos desactivados"
        elif self._puntos_canjeados:
            boton_canjear_texto = "Puntos canjeados"
        else:
            boton_canjear_texto = "Canjear puntos"

        return {
            "total":                    self.calcular_total(),
            "puntos":                   puntos,
            "descuento":                self.descuento_aplicado if tiene_descuento else 0.0,
            "header":                   f"{puntos} pts" if self.permite_puntos else "Cajero",
            "mostrar_descuento":        tiene_descuento,
            "boton_canjear_texto":      boton_canjear_texto,
            "boton_canjear_habilitado": boton_canjear_habilitado,
        }

    # ── Lógica de puntos ──────────────────────────────────────

    def previsualizar_canje_puntos(self):
        """
        Calcula cuántos puntos se usarían y cuánto descuento se aplicaría
        SIN modificar el estado. Útil para mostrar un preview al usuario.

        Regla: 100 puntos = 1 €. El descuento no puede superar el subtotal.
        Devuelve (puntos_necesarios, importe_descuento).
        """
        if not self.puede_canjear_puntos():
            return 0, 0.0
        subtotal          = self.calcular_subtotal()
        descuento         = min(self.puntos_disponibles / 100.0, subtotal)  # Tope = subtotal
        puntos_necesarios = int(round(descuento * 100))
        return puntos_necesarios, round(puntos_necesarios / 100.0, 2)

    def canjear_puntos(self):
        """
        Aplica el canje: fija el descuento y marca la bandera.
        Llamar solo si puede_canjear_puntos() es True (lo garantiza intentar_canjear_puntos).
        """
        if not self.puede_canjear_puntos():
            return
        puntos_necesarios, descuento = self.previsualizar_canje_puntos()
        self._descuento_aplicado = descuento
        self._puntos_canjeados   = True
        self._puntos_usados      = min(self.puntos_disponibles, puntos_necesarios)

    def intentar_canjear_puntos(self):
        """
        Versión segura de canjear_puntos: valida el estado antes de actuar.
        Devuelve (True, None) si se ha canjeado, o (False, mensaje_error) si no.
        El controlador usa el mensaje para mostrarlo en la UI.
        """
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

    # ── Finalización y abandono ───────────────────────────────

    def finalizar_pedido(self, total=None):
        """
        Persiste el pedido en BD y actualiza los puntos del usuario:
          1. Crea el pedido vía PedidoDao
          2. Descuenta los puntos usados en el canje (si los hay)
          3. Suma los puntos ganados por el pedido (10 puntos por euro)
          4. Vacía la cesta

        Devuelve (pedido_id, puntos_ganados).
        Lanza ValueError si la cesta está vacía o no hay sesión.
        """
        if not self.tiene_items():
            raise ValueError("No hay productos en la cesta.")
        if self._sesion is None:
            raise ValueError("No hay una sesion activa.")

        total_final = self.calcular_total() if total is None else float(total)
        pedido_id   = self._pedido_dao.crear(self._sesion, self.obtener_items(), total_final)

        puntos_ganados = 0
        if self.permite_puntos:
            # Descuenta los puntos canjeados (si los hubo)
            if self._puntos_usados:
                self._user_dao.actualizarPuntos(self._sesion.id_sesion, -self._puntos_usados)
                if hasattr(self._sesion, "consumir_puntos"):
                    self._sesion.consumir_puntos(self._puntos_usados)  # Actualiza el objeto en memoria

            # Suma los puntos ganados: 10 puntos por cada euro del total
            puntos_ganados = int(round(total_final * 10))
            if puntos_ganados > 0:
                self._user_dao.actualizarPuntos(self._sesion.id_sesion, puntos_ganados)
                if hasattr(self._sesion, "sumar_puntos"):
                    self._sesion.sumar_puntos(puntos_ganados)  # Actualiza el objeto en memoria

        self.vaciar_cesta()
        return pedido_id, puntos_ganados

    def intentar_finalizar_pedido(self):
        """
        Versión segura de finalizar_pedido para el controlador.
        Devuelve (True, (pedido_id, puntos_ganados, total)) o (False, mensaje_error).
        """
        if not self.tiene_items():
            return False, "Añade productos antes de finalizar."
        if self._sesion is None:
            return False, "No hay una sesion activa."
        total = self.calcular_total()
        pedido_id, puntos_ganados = self.finalizar_pedido(total)
        return True, (pedido_id, puntos_ganados, total)

    def intentar_abandonar_pedido(self):
        """
        Vacía la cesta si tiene ítems.
        Devuelve (True, None) o (False, mensaje_error).
        """
        if not self.tiene_items():
            return False, "No hay productos en la cesta."
        self.vaciar_cesta()
        return True, None

    def vaciar_cesta(self):
        """Resetea completamente el estado de la cesta (ítems, descuento y puntos)."""
        self._items.clear()
        self._descuento_aplicado = 0.0
        self._puntos_canjeados   = False
        self._puntos_usados      = 0

    # ── Historial ─────────────────────────────────────────────

    def snapshot_history(self):
        """
        Recupera el historial de pedidos del cliente activo desde la BD.
        Devuelve lista vacía si no hay sesión.
        """
        if self._sesion is None:
            return []
        return self._pedido_dao.listar(self._sesion)

    def obtener_historial(self):
        """Alias público de snapshot_history (usado por el controlador de historial)."""
        return self.snapshot_history()