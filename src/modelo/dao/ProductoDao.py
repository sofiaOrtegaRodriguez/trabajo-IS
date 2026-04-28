class ProductoDao:
    def listar(self):
        raise NotImplementedError("Metodo listar() no implementado")

    def crear(self, producto_vo):
        raise NotImplementedError("Metodo crear() no implementado")

    def actualizar(self, nombre_original, producto_vo):
        raise NotImplementedError("Metodo actualizar() no implementado")

    def eliminar(self, nombre_producto):
        raise NotImplementedError("Metodo eliminar() no implementado")

    def describir(self):
        raise NotImplementedError("Metodo describir() no implementado")
