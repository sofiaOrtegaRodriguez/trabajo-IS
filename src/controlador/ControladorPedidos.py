from src.modelo.vo.PedidoVo import PedidoVo


class ControladorPedidos:
    def __init__(self, ref_modelo):
        self._modelo = ref_modelo
        self._filtro_pedidos = "TODOS"

    def buscarPedidos(self):
        return self._modelo.listarTodosPedidos()

    def actualizarEstado(self, id, nuevo_estado):
        pedido = PedidoVo(id, "", "", nuevo_estado, "", "")
        return self._modelo.actualizarEstadoPedido(pedido)

    def filtrarPedidos(self, pedidos, estado="TODOS"):
        return self._modelo.filtrarPedidosPorEstado(pedidos, estado)

    def prepararPedidosVista(self, pedidos, estado="TODOS"):
        return self._modelo.prepararPedidosVista(pedidos, estado)

    def establecer_filtro(self, estado="TODOS"):
        self._filtro_pedidos = str(estado).strip().upper() or "TODOS"
        return self._filtro_pedidos

    def obtener_filtro(self):
        return self._filtro_pedidos

    def prepararPedidosVistaActual(self, pedidos=None):
        return self._modelo.prepararPedidosVistaActual(pedidos)

    def obtener_estados_pedido_permitidos(self):
        return self._modelo.obtenerEstadosPedidoPermitidos()

    def obtener_filtros_pedido_disponibles(self):
        return self._modelo.obtenerFiltrosPedidoDisponibles()
