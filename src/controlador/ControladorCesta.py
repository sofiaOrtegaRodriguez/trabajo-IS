class ControladorCesta:
    """
    Controlador de la cesta de la compra del cliente.

    Responsabilidad ÚNICA: hacer de fachada (patrón Facade) entre la capa
    de vistas y ServicioCesta, que es donde vive toda la lógica de negocio.

    Este controlador NO toma ninguna decisión propia:
      - No calcula precios.
      - No valida reglas de negocio.
      - No accede a la BD.
    Solo redirige cada llamada a self._servicio y devuelve el resultado.

    ¿Por qué existe si no hace nada propio?
      → Respeta MVC: la vista nunca habla directamente con la capa de servicio/modelo.
      → Permite cambiar la implementación de ServicioCesta sin tocar las vistas.
      → Centraliza el punto de entrada a la lógica de cesta.
    """

    def __init__(self, servicio_cesta):
        """
        Recibe por inyección de dependencias el ServicioCesta ya construido.
        El servicio es quien mantiene el estado real de la cesta (items, descuentos…).
        """
        self._servicio = servicio_cesta

    # ── Configuración de sesión y cliente ─────────────────────────────────────
    # Se llaman desde VentanaPrincipal/ControladorCliente al iniciar sesión
    # para que el servicio sepa a qué cliente y sesión pertenece la cesta.

    def set_cliente(self, cliente):
        """
        Inyecta el ClienteVo del usuario logueado en el servicio.
        Necesario para saber sus puntos disponibles, historial, etc.
        """
        self._servicio.set_cliente(cliente)

    def set_session(self, sesion):
        """
        Inyecta los datos de sesión activa (token, id_empleado…).
        El servicio los usa al finalizar pedidos o registrar operaciones.
        """
        self._servicio.set_session(sesion)

    # ── Propiedades de solo lectura — estado de puntos y descuentos ───────────
    # Son @property: se acceden como atributos (sin paréntesis) desde la vista.
    # Delegan directamente en el servicio para no duplicar estado.

    @property
    def permite_puntos(self):
        """True si el sistema tiene activado el canje de puntos de fidelidad."""
        return self._servicio.permite_puntos

    @property
    def puntos_disponibles(self):
        """Puntos de fidelidad que tiene el cliente en su cuenta (sin gastar)."""
        return self._servicio.puntos_disponibles

    @property
    def descuento_aplicado(self):
        """Importe de descuento ya aplicado a la cesta (resultado del canje)."""
        return self._servicio.descuento_aplicado

    @property
    def puntos_canjeados(self):
        """Puntos que el cliente ha canjeado en el pedido actual."""
        return self._servicio.puntos_canjeados

    @property
    def puntos_usados(self):
        """
        Alias semántico de puntos_canjeados.
        (Pueden representar conceptos ligeramente distintos según ServicioCesta;
        consultar allí si hay diferencia entre 'canjeados' y 'usados'.)
        """
        return self._servicio.puntos_usados

    # ── Consultas de estado — qué acciones están permitidas ahora ────────────
    # Devuelven bool. La vista los usa para habilitar/deshabilitar botones.

    def puede_canjear_puntos(self):
        """
        True si el cliente puede canjear puntos en este momento.
        Condiciones típicas: tiene puntos, no los ha canjeado ya, la cesta no está vacía.
        """
        return self._servicio.puede_canjear_puntos()

    def puede_finalizar_pedido(self):
        """
        True si se cumplen todas las condiciones para confirmar el pedido
        (ej: cesta no vacía, stock disponible, etc.).
        """
        return self._servicio.puede_finalizar_pedido()

    def puede_abandonar_pedido(self):
        """
        True si hay un pedido en curso que se puede cancelar/abandonar.
        Controla si el botón 'Cancelar pedido' debe estar activo.
        """
        return self._servicio.puede_abandonar_pedido()

    # ── Gestión de ítems de la cesta ─────────────────────────────────────────
    # CRUD básico sobre los productos dentro de la cesta.

    def add_item(self, product, amount=1):
        """
        Añade `amount` unidades de `product` a la cesta.
        Si el producto ya existe, incrementa su cantidad.
        Por defecto añade 1 unidad.
        """
        self._servicio.add_item(product, amount)

    def remove_item(self, product_id):
        """
        Elimina completamente el producto con ese id de la cesta,
        independientemente de la cantidad que haya.
        (Equivalente a eliminar_item — pueden ser sinónimos o diferir en validaciones.)
        """
        self._servicio.remove_item(product_id)

    def incrementar(self, product_id):
        """Suma 1 unidad al producto indicado dentro de la cesta."""
        self._servicio.incrementar(product_id)

    def decrementar(self, product_id):
        """
        Resta 1 unidad al producto indicado.
        Si llega a 0, el servicio decide si lo elimina o lo deja en 0.
        """
        self._servicio.decrementar(product_id)

    def eliminar_item(self, product_id):
        """
        Elimina el ítem de la cesta (botón 'Eliminar' en la fila del producto).
        Diferencia con remove_item: puede incluir confirmación o lógica extra en el servicio.
        """
        self._servicio.eliminar_item(product_id)

    # ── Consultas sobre el contenido de la cesta ─────────────────────────────

    def obtener_items(self):
        """
        Devuelve la lista de ítems actuales de la cesta (lista de VOs o dicts).
        La vista la usa para renderizar la tabla de productos añadidos.
        """
        return self._servicio.obtener_items()

    def cantidad_producto(self, product_id):
        """
        Devuelve cuántas unidades hay de ese producto en la cesta.
        Útil para mostrar el contador en el botón '+' de la carta.
        """
        return self._servicio.cantidad_producto(product_id)

    # ── Cálculos de precio ────────────────────────────────────────────────────

    def calcular_subtotal(self):
        """
        Suma de precios × cantidades SIN aplicar descuentos de puntos.
        Se muestra como 'Subtotal' en la vista de la cesta.
        """
        return self._servicio.calcular_subtotal()

    def calcular_total(self):
        """
        Total final = subtotal − descuento_aplicado.
        Es el importe que el cliente pagará realmente.
        """
        return self._servicio.calcular_total()

    def resumen_vista(self):
        """
        Devuelve un dict/objeto con todos los datos que la vista necesita
        para renderizar el resumen de la cesta de una sola vez
        (items, subtotal, descuento, total, puntos…).
        Evita que la vista llame a varios métodos por separado.
        """
        return self._servicio.resumen_vista()

    # ── Puntos de fidelidad ───────────────────────────────────────────────────

    def previsualizar_canje_puntos(self):
        """
        Calcula y devuelve cuánto descuento obtendrían los puntos disponibles
        SIN aplicarlo todavía. Se usa para mostrar el tooltip/info antes de confirmar.
        """
        return self._servicio.previsualizar_canje_puntos()

    def canjear_puntos(self):
        """
        Aplica el canje de puntos: descuenta del total y marca los puntos como usados.
        No devuelve nada; la vista debe llamar a calcular_total() para refrescar.
        """
        self._servicio.canjear_puntos()

    def intentar_canjear_puntos(self):
        """
        Versión 'segura' de canjear_puntos: comprueba internamente si se puede
        y devuelve un resultado (bool o mensaje) en lugar de lanzar excepción.
        Preferible cuando la vista no quiere gestionar try/except.
        """
        return self._servicio.intentar_canjear_puntos()

    # ── Ciclo de vida del pedido ──────────────────────────────────────────────

    def finalizar_pedido(self, total=None):
        """
        Confirma y registra el pedido en la BD.
        - total: si se pasa, sobreescribe el cálculo interno (útil para casos especiales).
        - Devuelve el resultado del servicio (¿pedido creado? ¿id? ¿error?).
        Después de esto la cesta queda vacía y los puntos se actualizan.
        """
        return self._servicio.finalizar_pedido(total)

    def intentar_finalizar_pedido(self):
        """
        Versión 'segura' de finalizar_pedido: valida condiciones antes de ejecutar
        y devuelve un resultado sin propagar excepciones.
        La vista muestra el resultado directamente sin necesitar try/except.
        """
        return self._servicio.intentar_finalizar_pedido()

    def vaciar_cesta(self):
        """
        Elimina todos los ítems de la cesta y resetea descuentos y puntos canjeados.
        Se llama al cerrar sesión, al abandonar pedido, o tras finalizar con éxito.
        """
        self._servicio.vaciar_cesta()

    def intentar_abandonar_pedido(self):
        """
        Cancela el pedido en curso (si existe) y vacía la cesta.
        Versión 'segura': devuelve resultado en lugar de lanzar excepciones.
        Se conecta al botón 'Cancelar pedido' de la vista.
        """
        return self._servicio.intentar_abandonar_pedido()

    # ── Historial ─────────────────────────────────────────────────────────────

    def snapshot_history(self):
        """
        Guarda un 'snapshot' del estado actual de la cesta en el historial interno.
        Se llama en momentos clave (ej: antes de finalizar) para poder reconstruir
        el pedido si algo falla o para mostrarlo en el historial de sesión.
        """
        return self._servicio.snapshot_history()

    def obtener_historial(self):
        """
        Devuelve la lista de pedidos anteriores del cliente (historial de BD).
        La vista lo usa para mostrar el historial en el perfil del usuario.
        """
        return self._servicio.obtener_historial()