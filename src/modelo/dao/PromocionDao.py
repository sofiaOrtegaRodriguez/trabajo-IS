class PromocionDao:
    def listar(self):
        raise NotImplementedError("Metodo listar() no implementado")

    def crear(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        raise NotImplementedError("Metodo crear() no implementado")

    def eliminar(self, id_promocion):
        raise NotImplementedError("Metodo eliminar() no implementado")
