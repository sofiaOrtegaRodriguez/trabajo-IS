from datetime import date

from src.modelo.vo.ProductoVo import ProductoVo
from src.modelo.vo.PromocionVo import PromocionVo


class ControladorProductos:
    def __init__(self, ref_modelo):
        self._modelo = ref_modelo

    def listarProductos(self):
        return self._modelo.listarProductos()

    def listarProductosCarta(self):
        grouped = {
            "sushi": [],
            "fritos": [],
            "bebidas": [],
            "postres": [],
            "promociones": [],
        }

        productos = self._modelo.listarProductos()
        promociones_activas = self._promociones_activas_por_producto()

        for producto in productos:
            if int(producto.stock) < 1:
                continue

            categoria = self._normalize_category(producto.categoria)
            if categoria not in grouped:
                continue

            product_info = {
                "id": producto.nombre,
                "nombre": producto.nombre,
                "precio": float(producto.precio),
                "categoria": categoria,
                "precio_original": float(producto.precio),
                "promocion_hasta": "",
                "promocion_descuento": 0,
            }

            promo = promociones_activas.get(producto.nombre)
            if promo is not None:
                discounted_price = round(float(producto.precio) * (100 - promo.descuento) / 100, 2)
                product_info["precio"] = discounted_price
                product_info["precio_original"] = float(producto.precio)
                product_info["promocion_hasta"] = promo.fecha_fin.strftime("%d/%m/%Y")
                product_info["promocion_descuento"] = int(promo.descuento)
                grouped["promociones"].append(product_info)
            else:
                grouped[categoria].append(product_info)

        return grouped

    def describirProductos(self):
        return self._modelo.describirProductos()

    def crearProducto(self, nombre, precio, ingredientes, disponible, stock, categoria):
        producto = ProductoVo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self._modelo.crearProducto(producto)

    def actualizarProducto(self, nombre_original, nombre, precio, ingredientes, disponible, stock, categoria):
        producto = ProductoVo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self._modelo.actualizarProducto(nombre_original, producto)

    def eliminarProducto(self, nombre_producto):
        return self._modelo.eliminarProducto(nombre_producto)

    def listarPromociones(self):
        return self._modelo.listarPromociones()

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        promocion = PromocionVo(None, descuento, fecha_inicio, fecha_fin, nombre_producto)
        return self._modelo.crearPromocion(
            promocion.descuento,
            promocion.fecha_inicio,
            promocion.fecha_fin,
            promocion.nombre_producto,
        )

    def eliminarPromocion(self, id_promocion):
        return self._modelo.eliminarPromocion(id_promocion)

    def _normalize_category(self, categoria):
        normalized = str(categoria).strip().lower()
        aliases = {
            "sushi": "sushi",
            "fritos": "fritos",
            "postres": "postres",
            "bebidas": "bebidas",
            "bebida": "bebidas",
        }
        return aliases.get(normalized, "")

    def _promociones_activas_por_producto(self):
        today = date.today()
        promos_by_product = {}

        for promocion in self._modelo.listarPromociones():
            if not promocion.nombre_producto:
                continue
            if promocion.fecha_fin <= today:
                continue
            current = promos_by_product.get(promocion.nombre_producto)
            if current is None or promocion.fecha_fin > current.fecha_fin:
                promos_by_product[promocion.nombre_producto] = promocion
        return promos_by_product
