class PedidoDetalleVo:
    def __init__(self, nombre_producto, cantidad, subtotal):
        self.__nombre_producto = nombre_producto
        self.__cantidad = cantidad
        self.__subtotal = subtotal

    @property
    def nombre_producto(self):
        return self.__nombre_producto

    @property
    def cantidad(self):
        return self.__cantidad

    @property
    def subtotal(self):
        return self.__subtotal


class PedidoVo:
    def __init__(self, id_pedido, fecha, hora, estado, productos, total):
        self.__id = id_pedido
        self.__fecha = fecha
        self.__hora = hora
        self.__estado = estado
        self.__productos = productos
        self.__total = total

    @property
    def id(self):
        return self.__id

    @property
    def fecha(self):
        return self.__fecha

    @property
    def hora(self):
        return self.__hora

    @property
    def estado(self):
        return self.__estado

    @property
    def productos(self):
        return self.__productos

    @property
    def total(self):
        return self.__total


# Compatibilidad con el código existente
PedidoHistorico = PedidoVo
PedidoDetalleHistorico = PedidoDetalleVo
