from src.modelo.vo.ProductoVo import ProductoVo
from src.modelo.vo.PromocionVo import PromocionVo


class ControladorProductos:
    def __init__(self, ref_modelo):
        self._modelo = ref_modelo

    def listarProductos(self):
        return self._modelo.listarProductos()

    def listarProductosCarta(self):
        return self._modelo.listarProductosCarta()

    def describirProductos(self):
        return self._modelo.describirProductos()

    def obtenerCategoriasAdmin(self):
        return self._modelo.obtenerCategoriasAdmin()

    def crearProducto(self, nombre, precio, ingredientes, disponible, stock, categoria):
        producto = ProductoVo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self._modelo.crearProductoValidado(
            producto.nombre,
            producto.precio,
            producto.ingredientes,
            producto.disponible,
            producto.stock,
            producto.categoria,
        )

    def crearProductoValidado(self, nombre, precio, ingredientes, disponible, stock, categoria):
        return self._modelo.crearProductoValidado(nombre, precio, ingredientes, disponible, stock, categoria)

    def actualizarProducto(self, nombre_original, nombre, precio, ingredientes, disponible, stock, categoria):
        producto = ProductoVo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self._modelo.actualizarProductoValidado(
            nombre_original,
            producto.nombre,
            producto.precio,
            producto.ingredientes,
            producto.disponible,
            producto.stock,
            producto.categoria,
        )

    def actualizarProductoValidado(self, nombre_original, nombre, precio, ingredientes, disponible, stock, categoria):
        return self._modelo.actualizarProductoValidado(nombre_original, nombre, precio, ingredientes, disponible, stock, categoria)

    def eliminarProducto(self, nombre_producto):
        return self._modelo.eliminarProducto(nombre_producto)

    def listarPromociones(self):
        return self._modelo.listarPromociones()

    def prepararPromocionesVista(self, promociones=None):
        return self._modelo.prepararPromocionesVista(promociones)

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        promocion = PromocionVo(None, descuento, fecha_inicio, fecha_fin, nombre_producto)
        return self._modelo.crearPromocionValidada(
            promocion.descuento,
            promocion.fecha_inicio,
            promocion.fecha_fin,
            promocion.nombre_producto,
        )

    def crearPromocionValidada(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        return self._modelo.crearPromocionValidada(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def eliminarPromocion(self, id_promocion):
        return self._modelo.eliminarPromocion(id_promocion)
