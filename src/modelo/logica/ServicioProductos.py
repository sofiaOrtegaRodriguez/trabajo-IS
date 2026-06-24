from src.modelo.dao.ProductoDaoJDBC import ProductoDaoJDBC
from src.modelo.vo.ProductoVo import ProductoVo

class ServicioProductos:
    """
    Servicio de lógica de negocio para productos.

    Capa intermedia entre el controlador y ProductoDaoJDBC.
    Responsabilidades:
      - Delegar operaciones CRUD en el DAO
      - Validar datos antes de persistirlos (_validar_producto_datos)
      - Construir el VO antes de enviarlo al DAO (_construir_producto_vo)
      - Normalizar categorías para que sean consistentes en la BD

    Patrón: igual que ServicioPromociones, cada operación tiene dos versiones:
      - Sin validar (crearProducto, actualizarProducto): persistencia pura
      - Validada (crearProductoValidado, actualizarProductoValidado): valida + persiste
    """

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PÚBLICOS: CRUD
    # ─────────────────────────────────────────────────────────────

    def listarProductos(self):
        """
        Devuelve la lista de VOs de producto tal como los entrega el DAO.
        Sin transformación adicional.
        """
        return ProductoDaoJDBC().listar()

    def crearProducto(self, producto_vo):
        """
        Crea un producto en la BD SIN validar los datos.
        Recibe directamente un ProductoVo ya construido y lo pasa al DAO.
        """
        return ProductoDaoJDBC().crear(producto_vo)

    def crearProductoValidado(self, nombre, precio, ingredientes, disponible, stock, categoria):
        """
        Valida los datos, construye el VO y crea el producto en la BD.
        Es el método que debe llamar el controlador cuando el usuario
        rellena el formulario y pulsa "Añadir producto".

        Lanza ValueError con mensaje descriptivo si algún dato no es válido.
        """
        self._validar_producto_datos(nombre, precio, ingredientes, disponible, stock, categoria)
        producto = self._construir_producto_vo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self.crearProducto(producto)

    def actualizarProducto(self, nombre_original, producto_vo):
        """
        Actualiza un producto en la BD SIN validar los datos.
        Necesita el nombre_original para identificar el registro en la BD,
        ya que el nombre puede cambiar durante la edición.
        """
        return ProductoDaoJDBC().actualizar(nombre_original, producto_vo)

    def actualizarProductoValidado(self, nombre_original, nombre, precio, ingredientes, disponible, stock, categoria):
        """
        Valida los datos, construye el VO y actualiza el producto en la BD.
        Es el método que debe llamar el controlador cuando el usuario
        edita un producto y pulsa "Guardar cambios".

        nombre_original: nombre del producto antes de la edición (clave para el UPDATE en BD)
        Los demás parámetros son los nuevos valores del formulario.
        """
        self._validar_producto_datos(nombre, precio, ingredientes, disponible, stock, categoria)
        producto = self._construir_producto_vo(nombre, precio, ingredientes, disponible, stock, categoria)
        return self.actualizarProducto(nombre_original, producto)

    def eliminarProducto(self, nombre_producto):
        """
        Elimina el producto con el nombre indicado.
        Delega directamente en el DAO sin validación adicional.
        """
        return ProductoDaoJDBC().eliminar(nombre_producto)

    def describirProductos(self):
        """
        Devuelve la descripción del esquema de la tabla PRODUCTOS
        (columnas, tipos, etc.) tal como la entrega el DAO.
        Se usa para comprobar si la BD tiene columna de categoría.
        """
        return ProductoDaoJDBC().describir()

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS: validación
    # ─────────────────────────────────────────────────────────────

    def _validar_producto_datos(self, nombre, precio, ingredientes, disponible, stock, categoria):
        """
        Valida todos los campos del formulario de producto.
        Lanza ValueError en el primer error encontrado.

        Reglas de validación:
          1. nombre no puede estar vacío
          2. ingredientes no pueden estar vacíos
          3. precio debe ser mayor que 0
          4. stock no puede ser negativo
          5. disponible debe ser uno de los valores reconocidos (Y/N y variantes)
          6. categoría debe ser una de las 4 categorías válidas del restaurante
        """
        # Normaliza para comparar sin espacios ni mayúsculas
        nombre = str(nombre).strip()
        ingredientes = str(ingredientes).strip()
        categoria_norm = self._normalize_category(categoria)

        # Regla 1: nombre obligatorio
        if not nombre:
            raise ValueError("El nombre del producto es obligatorio.")

        # Regla 2: ingredientes obligatorios
        if not ingredientes:
            raise ValueError("Los ingredientes son obligatorios.")

        # Regla 3: precio mayor que cero
        if float(precio) <= 0:
            raise ValueError("El precio debe ser mayor que cero.")

        # Regla 4: stock no negativo
        if int(stock) < 0:
            raise ValueError("El stock no puede ser negativo.")

        # Regla 5: disponible debe ser un valor reconocido
        # Se aceptan varias formas para mayor compatibilidad con la BD y el formulario
        if str(disponible).strip().upper() not in ("Y", "N", "SI", "S", "YES", "TRUE", "1", "0"):
            raise ValueError("El valor de disponible no es valido.")

        # Regla 6: categoría debe ser una de las 4 válidas del restaurante
        # _normalize_category devuelve "" si no reconoce la categoría
        if categoria_norm not in ("sushi", "fritos", "bebidas", "postres"):
            raise ValueError("La categoria indicada no es valida.")

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS: utilidades
    # ─────────────────────────────────────────────────────────────

    def _normalize_category(self, categoria):
        """
        Normaliza el nombre de una categoría a su forma canónica en minúsculas.

        Convierte el texto a minúsculas y sin espacios, luego lo busca en
        el diccionario de alias. Si no se reconoce, devuelve "" para que
        la validación pueda detectarlo como categoría inválida.

        Ejemplos:
          "Bebidas" → "bebidas"
          "bebida"  → "bebidas"  (alias: singular → plural)
          "Sushi"   → "sushi"
          "pizza"   → ""         (no reconocida)
        """
        normalized = str(categoria).strip().lower()
        aliases = {
            "sushi": "sushi",
            "fritos": "fritos",
            "postres": "postres",
            "bebidas": "bebidas",
            "bebida": "bebidas",   # alias: forma singular aceptada
        }
        return aliases.get(normalized, "")  # "" si no está en el dict

    def _construir_producto_vo(self, nombre, precio, ingredientes, disponible, stock, categoria):
        """
        Construye y devuelve un ProductoVo con los datos recibidos,
        aplicando la normalización de categoría antes de guardarlo.

        La categoría se almacena capitalizada (ej. "Bebidas") para
        que se muestre correctamente en la vista y en la BD.
        Si la categoría no se reconoce (caso raro tras validar), se usa
        el valor original sin transformar.

        El import de ProductoVo es local (dentro del método) para evitar
        importaciones circulares en el arranque de la aplicación.
        """
        

        categoria_final = self._normalize_category(categoria)
        # capitalize() → primera letra en mayúscula, resto en minúscula
        # Si categoria_final es "" (no reconocida), usa el valor original como fallback
        categoria_label = categoria_final.capitalize() if categoria_final else str(categoria).strip()

        return ProductoVo(nombre, precio, ingredientes, disponible, stock, categoria_label)