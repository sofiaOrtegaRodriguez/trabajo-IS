from src.modelo.vo.PedidoVo import PedidoVo


class ControladorPedidos:
    def __init__(self, ref_modelo):
        self._modelo = ref_modelo
        self._filtro_pedidos = "TODOS" #Filtro inicial para mostrar todos los pedidos

    def buscarPedidos(self):
        """Devuelve la lista de todos los pedidos desde el modelo."""
        return self._modelo.listarTodosPedidos()

    def actualizarEstado(self, id, nuevo_estado):
        """Actualiza el estado de un pedido dado su ID y el nuevo estado."""
        pedido = PedidoVo(id, "", "", nuevo_estado, "", "")
        return self._modelo.actualizarEstadoPedido(pedido)

    def filtrarPedidos(self, pedidos, estado="TODOS"):
        """Filtra los pedidos por estado."""
        return self._modelo.filtrarPedidosPorEstado(pedidos, estado)

    def prepararPedidosVista(self, pedidos, estado="TODOS"):
        """Prepara la vista de los pedidos filtrados."""
        return self._modelo.prepararPedidosVista(pedidos, estado)

    def establecer_filtro(self, estado="TODOS"):
        """Establece el filtro para mostrar pedidos por estado."""
        self._filtro_pedidos = str(estado).strip().upper() or "TODOS"
        return self._filtro_pedidos

    def obtener_filtro(self):
        """Devuelve el filtro actual para mostrar pedidos por estado."""
        return self._filtro_pedidos

    def prepararPedidosVistaActual(self, pedidos=None):
        """Prepara la vista de los pedidos según el filtro actual."""
        return self._modelo.prepararPedidosVistaActual(pedidos)

    def obtener_estados_pedido_permitidos(self):
        """Devuelve la lista de estados de pedido permitidos desde el modelo."""
        return self._modelo.obtenerEstadosPedidoPermitidos()

    def obtener_filtros_pedido_disponibles(self):
        """Devuelve la lista de filtros de pedido disponibles desde el modelo."""
        return self._modelo.obtenerFiltrosPedidoDisponibles()
