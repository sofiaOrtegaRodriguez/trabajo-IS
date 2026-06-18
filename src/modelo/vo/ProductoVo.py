"""
    Value Object (VO) que representa un producto

    Su fucnión es encapsular todos los datos de un producto en un único objeto para poder transportarlo
    entre las distintas capas de la aplicación (vista, controlador y modelo (DAO))

    VO no tiene lógica de negocio ni acceso a la BD, solamente almacena la info del producto
"""

class ProductoVo:
    def __init__(self, nombre, precio, ingredientes, disponible, stock, categoria=""):

        """
            Parámetros:
                nombre: nombre del producto
                precio: precio de venta
                ingredientes: ingredientes que componen el producto
                disponible: indica si el producto está disponible
                stock: cantidad disponible en inventario
                categoria: categoría a la que pertenece (Sushi, Fritos, Bebidas, Postres, etc.)

            Los atributos se almacenan como privados (__atributo)
            para evitar modificaciones directas desde el exterior.
        """
        self.__nombre = nombre
        self.__precio = precio
        self.__ingredientes = ingredientes
        self.__disponible = disponible
        self.__stock = stock
        self.__categoria = categoria

    #getter nombre
    @property
    def nombre(self):
        #devuelve el nombre
        return self.__nombre

    #getter precio
    @property
    def precio(self):
        #devuelve el precio
        return self.__precio

    #getter ingredientes
    @property
    def ingredientes(self):
        #devuelve los ingredientes
        return self.__ingredientes

    #getter si está disponible
    @property
    def disponible(self):
        #devuelve si está disponible
        return self.__disponible

    #getter del stock
    @property
    def stock(self):
        #devuelve si hay stock
        return self.__stock

    #getter de categoría
    @property
    def categoria(self):
        #nos devuelve la categoría del producto
        return self.__categoria
