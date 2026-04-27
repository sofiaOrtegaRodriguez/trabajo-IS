from src.modelo.Logica import Logica
from src.modelo.vo.PedidoVo import PedidoVo

class ControladorPedidos:
    def __init__(self):
        self._modelo = Logica()

    def buscarPedidos(self):
        return self._modelo.listarTodosPedidos()
    
    def actualizarEstado(self, id, nuevo_estado):
        pedido = PedidoVo(id,"","", nuevo_estado, "","")
        return self._modelo.actualizarEstadoPedido(pedido)