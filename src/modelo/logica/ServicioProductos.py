from src.modelo.dao.ProductoDaoJDBC import ProductoDaoJDBC


class ServicioProductos:
    def listarProductos(self):
        return ProductoDaoJDBC().listar()

    def crearProducto(self, producto_vo):
        return ProductoDaoJDBC().crear(producto_vo)

    def crearProductoValidado(self, nombre, precio, ingredientes, disponible, stock, categoria):
        self._validar_producto_datos(nombre, precio, ingredientes, disponible, stock, categoria)
        producto = self._construir_producto_vo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self.crearProducto(producto)

    def actualizarProducto(self, nombre_original, producto_vo):
        return ProductoDaoJDBC().actualizar(nombre_original, producto_vo)

    def actualizarProductoValidado(self, nombre_original, nombre, precio, ingredientes, disponible, stock, categoria):
        self._validar_producto_datos(nombre, precio, ingredientes, disponible, stock, categoria)
        producto = self._construir_producto_vo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self.actualizarProducto(nombre_original, producto)

    def eliminarProducto(self, nombre_producto):
        return ProductoDaoJDBC().eliminar(nombre_producto)

    def describirProductos(self):
        return ProductoDaoJDBC().describir()

    def _validar_producto_datos(self, nombre, precio, ingredientes, disponible, stock, categoria):
        nombre = str(nombre).strip()
        ingredientes = str(ingredientes).strip()
        categoria_norm = self._normalize_category(categoria)
        if not nombre:
            raise ValueError("El nombre del producto es obligatorio.")
        if not ingredientes:
            raise ValueError("Los ingredientes son obligatorios.")
        if float(precio) <= 0:
            raise ValueError("El precio debe ser mayor que cero.")
        if int(stock) < 0:
            raise ValueError("El stock no puede ser negativo.")
        if str(disponible).strip().upper() not in ("Y", "N", "SI", "S", "YES", "TRUE", "1", "0"):
            raise ValueError("El valor de disponible no es valido.")
        if categoria_norm not in ("sushi", "fritos", "bebidas", "postres"):
            raise ValueError("La categoria indicada no es valida.")

    def _normalize_category(self, categoria):
        normalized = str(categoria).strip().lower()
        aliases = {"sushi": "sushi", "fritos": "fritos", "postres": "postres", "bebidas": "bebidas", "bebida": "bebidas"}
        return aliases.get(normalized, "")

    def _construir_producto_vo(self, nombre, precio, ingredientes, disponible, stock, categoria):
        from src.modelo.vo.ProductoVo import ProductoVo
        categoria_final = self._normalize_category(categoria)
        categoria_label = categoria_final.capitalize() if categoria_final else str(categoria).strip()
        return ProductoVo(nombre, precio, ingredientes, disponible, stock, categoria_label)
