# Value Object (VO) que representa una promoción.

# Su función es encapsular toda la información relacionada
# con una promoción en un único objeto para transportarla
# entre las distintas capas de la aplicación.

# No contiene lógica de negocio ni acceso a base de datos, únicamente almacena datos.

class PromocionVo:
    def __init__(self, id_promocion, descuento, fecha_inicio, fecha_fin, nombre_producto=""):
        """
            Parámetros:
                id_promocion: identificador único de la promoción.
                descuento: porcentaje de descuento aplicado.
                fecha_inicio: fecha en la que comienza la promoción.
                fecha_fin: fecha en la que finaliza la promoción.
                nombre_producto: producto al que se aplica la promoción.

            Los atributos se almacenan como privados (__atributo)
            para evitar modificaciones directas desde el exterior.
        """
        self.__id_promocion = id_promocion
        self.__descuento = descuento
        self.__fecha_inicio = fecha_inicio
        self.__fecha_fin = fecha_fin
        self.__nombre_producto = nombre_producto

    #getter id_promoción
    @property
    def id_promocion(self):
        #devuelve el id de la promoción
        return self.__id_promocion

    #getter de descuento
    @property
    def descuento(self):
        #devuelve el desceunte
        return self.__descuento

    #getter de la fecha de inicio
    @property
    def fecha_inicio(self):
        #devuelve la fecha de inicio
        return self.__fecha_inicio

    #getter de la fecha de fin
    @property
    def fecha_fin(self):
        #devuelve la fecha de fin
        return self.__fecha_fin

    #getter nombre de producto
    @property
    def nombre_producto(self):
        #devuelve el nombre del producto
        return self.__nombre_producto
