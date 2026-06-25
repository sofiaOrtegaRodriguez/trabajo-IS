from src.modelo.vo.ProductoVo import ProductoVo
from src.modelo.vo.PromocionVo import PromocionVo


class ControladorProductos:
    """
    Fachada entre ControladorAdmin y el modelo para productos y promociones.
    No contiene lógica propia: delega todo en self._modelo.

    Patrón doble en crear/actualizar:
      - crearProducto / actualizarProducto → pasan primero por el VO (normaliza tipos)
      - crearProductoValidado / actualizarProductoValidado → van directo al modelo (datos ya tipados)
    """

    def __init__(self, ref_modelo):
        self._modelo = ref_modelo

    # ── Consultas ─────────────────────────────────────────────────────────────

    def listarProductos(self):
        """Todos los productos (vista admin: incluye stock, disponibilidad…)."""
        return self._modelo.listarProductos()

    def listarProductosCarta(self):
        """Solo productos visibles para el cliente (disponible=True, stock>0)."""
        return self._modelo.listarProductosCarta()

    def describirProductos(self):
        """Schema de la tabla PRODUCTOS (ej: si existe columna 'categoria')."""
        return self._modelo.describirProductos()

    def obtenerCategoriasAdmin(self):
        """Lista de categorías válidas para el formulario de admin."""
        return self._modelo.obtenerCategoriasAdmin()

    # ── CRUD productos ────────────────────────────────────────────────────────

    def crearProducto(self, nombre, precio, ingredientes, disponible, stock, categoria):
        """Construye el VO (normaliza tipos) y crea el producto en BD."""
        producto = ProductoVo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self._modelo.crearProductoValidado(
            producto.nombre, producto.precio, producto.ingredientes,
            producto.disponible, producto.stock, producto.categoria,
        )

    def crearProductoValidado(self, nombre, precio, ingredientes, disponible, stock, categoria):
        """Versión directa sin VO: usar cuando los datos ya están tipados."""
        return self._modelo.crearProductoValidado(nombre, precio, ingredientes, disponible, stock, categoria)

    def actualizarProducto(self, nombre_original, nombre, precio, ingredientes, disponible, stock, categoria):
        """
        Construye el VO y actualiza el producto en BD.
        nombre_original es la clave para encontrarlo (el nombre puede cambiar).
        """
        producto = ProductoVo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self._modelo.actualizarProductoValidado(
            nombre_original,
            producto.nombre, producto.precio, producto.ingredientes,
            producto.disponible, producto.stock, producto.categoria,
        )

    def actualizarProductoValidado(self, nombre_original, nombre, precio, ingredientes, disponible, stock, categoria):
        """Versión directa sin VO."""
        return self._modelo.actualizarProductoValidado(
            nombre_original, nombre, precio, ingredientes, disponible, stock, categoria
        )

    def eliminarProducto(self, nombre_producto):
        return self._modelo.eliminarProducto(nombre_producto)

    # ── Promociones ───────────────────────────────────────────────────────────

    def listarPromociones(self):
        return self._modelo.listarPromociones()

    def prepararPromocionesVista(self, promociones=None):
        """Transforma los VOs al formato que espera la tabla de la vista."""
        return self._modelo.prepararPromocionesVista(promociones)

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        """Construye el VO (id=None, lo asigna la BD) y persiste la promoción."""
        promocion = PromocionVo(None, descuento, fecha_inicio, fecha_fin, nombre_producto)
        return self._modelo.crearPromocionValidada(
            promocion.descuento, promocion.fecha_inicio,
            promocion.fecha_fin, promocion.nombre_producto,
        )

    def crearPromocionValidada(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        """Versión directa sin VO."""
        return self._modelo.crearPromocionValidada(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def eliminarPromocion(self, id_promocion):
        """Las promociones se identifican por id numérico, no por nombre."""
        return self._modelo.eliminarPromocion(id_promocion)