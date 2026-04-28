class PedidoDao:
    def crear(self, sesion, items, total):
        raise NotImplementedError("Metodo crear() no implementado")

    def listar(self, sesion):
        raise NotImplementedError("Metodo listar() no implementado")

    def listarTiempoReal(self):
        raise NotImplementedError("Metodo listarTiempoReal() no implementado")

    def modificarEstado(self, pedido):
        raise NotImplementedError("Metodo modificarEstado() no implementado")
