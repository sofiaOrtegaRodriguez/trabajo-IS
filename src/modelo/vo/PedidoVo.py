
# clase que representa el detalle de un producto dentro de un pedido
# cada línea del pedido: qué prod, cuántos y cuanto suma

class PedidoDetalleVo:
    def __init__(self, nombre_producto, cantidad, subtotal):
        self.__nombre_producto = nombre_producto # nombre del producto pedido
        self.__cantidad = cantidad # cantidad de unidades de ese producto
        self.__subtotal = subtotal # precio total de esa línea (precio x cant)

    # devuelve el nombre 
    @property
    def nombre_producto(self):
        return self.__nombre_producto

    # devuelve la cantidad pedida
    @property
    def cantidad(self):
        return self.__cantidad

    #  devuelve el subtotal de esa línea del pedido
    @property
    def subtotal(self):
        return self.__subtotal

# clase que representa un pedido completo con todos sus datos
class PedidoVo:
    def __init__(self, id_pedido, fecha, hora, estado, productos, total, usuario=None):
        self.__id = id_pedido # identificador único del pedido en la BD
        self.__fecha = fecha # fecha en la que se realizó el pedido
        self.__hora = hora # hora en la que se realizó el pedido
        self.__estado = estado # estado actual del pedido
        self.__productos = productos # lista de PedidoDetalleVo con los productos del pedido
        self.__total = total # importe total del pedido
        self.__usuario = usuario # usuaario que realizó el pedido (opcional)

    @property
    def id(self):
        return self.__id # devuelve el id del pedido

    @property
    def fecha(self):
        return self.__fecha # devuelve la fecha del pedido

    @property
    def hora(self):
        return self.__hora # devuelve la hora del pedido

    @property
    def estado(self):
        return self.__estado # devuelve el estado del pedido

    @property
    def productos(self):
        return self.__productos # devuelve la lista de productos (PedidoDetalleVo) del pedido

    @property
    def total(self):
        return self.__total # devuelve el total del pedido

    @property
    def usuario(self):
        return self.__usuario # devuelve el usuario que realizó el pedido