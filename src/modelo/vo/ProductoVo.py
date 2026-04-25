class ProductoVo:
    def __init__(self, nombre, precio, ingredientes, disponible, stock, categoria=""):
        self.__nombre = nombre
        self.__precio = precio
        self.__ingredientes = ingredientes
        self.__disponible = disponible
        self.__stock = stock
        self.__categoria = categoria

    @property
    def nombre(self):
        return self.__nombre

    @property
    def precio(self):
        return self.__precio

    @property
    def ingredientes(self):
        return self.__ingredientes

    @property
    def disponible(self):
        return self.__disponible

    @property
    def stock(self):
        return self.__stock

    @property
    def categoria(self):
        return self.__categoria
