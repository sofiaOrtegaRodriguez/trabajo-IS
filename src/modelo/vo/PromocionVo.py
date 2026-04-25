class PromocionVo:
    def __init__(self, id_promocion, descuento, fecha_inicio, fecha_fin, nombre_producto=""):
        self.__id_promocion = id_promocion
        self.__descuento = descuento
        self.__fecha_inicio = fecha_inicio
        self.__fecha_fin = fecha_fin
        self.__nombre_producto = nombre_producto

    @property
    def id_promocion(self):
        return self.__id_promocion

    @property
    def descuento(self):
        return self.__descuento

    @property
    def fecha_inicio(self):
        return self.__fecha_inicio

    @property
    def fecha_fin(self):
        return self.__fecha_fin

    @property
    def nombre_producto(self):
        return self.__nombre_producto
