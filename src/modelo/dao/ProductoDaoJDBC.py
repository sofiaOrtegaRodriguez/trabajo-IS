from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.vo.ProductoVo import ProductoVo


class ProductoDaoJDBC(ConexionSQLServer):
    #Columnas base de la tabla PRODUCTOS
    BASE_COLUMNS = ("Nombre", "Precio", "Ingredientes", "Disponible", "Stock") 
    CATEGORY_COLUMNS = ("Categorias", "Categoria")

    def listar(self):
        """Devuelve una lista de ProductoVo con todos los productos en la base de datos."""
        cursor = self.getCursor()
        try:
            schema = self._get_schema_info(cursor) #se obtiene la información del esquema para saber si existe una columna de categoria
            select_parts = ["[Nombre]", "[Precio]", "[Ingredientes]", "[Disponible]", "[Stock]", self._category_select(schema)]
            cursor.execute(
                f"""
                SELECT {", ".join(select_parts)}
                FROM PRODUCTOS
                ORDER BY Nombre
                """
            ) #ejecuta la consulta SQL para obtener los productos
            return [
                ProductoVo(row.Nombre, float(row.Precio), row.Ingredientes, row.Disponible, int(row.Stock), getattr(row, "Categoria", "") or "")
                for row in cursor.fetchall()
            ] #devuelve una lista de ProductoVo creada a partir de los resultados de la consulta
        except Exception as exc:
            raise RuntimeError(f"No se pudieron cargar los productos: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def crear(self, producto_vo):
        """Crea un nuevo producto en la base de datos a partir de un ProductoVo dado."""
        cursor = self.getCursor()
        try:
            schema = self._get_schema_info(cursor) #se obtiene la información del esquema para saber si existe una columna de categoria
            columns = list(self.BASE_COLUMNS)
            values = [producto_vo.nombre, producto_vo.precio, producto_vo.ingredientes, self._normalize_yes_no(producto_vo.disponible), producto_vo.stock]
            if schema["category_column"]: #si existe una columna de categoria, se añade a la lista de columnas y valores a insertar
                columns.append(schema["category_column"])
                values.append(producto_vo.categoria)
            elif producto_vo.categoria:
                raise ValueError("La base de datos actual no tiene columna de categoria en PRODUCTOS.")
            #Se crean los placeholders para la consulta SQL, uno por cada columna a insertar
            placeholders = ", ".join("?" for _ in columns) 
            #Se colocan los nombres de las columnas entre corchetes para evitar problemas con palabras reservadas o espacios,
            #y se ejecuta la consulta SQL para insertar el nuevo producto
            quoted_columns = ", ".join(self._quote_identifier(column) for column in columns)
            cursor.execute(f"INSERT INTO PRODUCTOS ({quoted_columns}) VALUES ({placeholders})", values)
            self.conexion.commit()
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback()
            if self._is_constraint_error(exc):
                raise ValueError("No se pudo crear el producto. Revisa si el nombre ya existe o si los datos incumplen una restriccion.") from exc
            raise
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def actualizar(self, nombre_original, producto_vo):
        """Actualiza un producto existente identificado por su nombre original, con los datos de un ProductoVo dado."""
        cursor = self.getCursor()
        try:
            schema = self._get_schema_info(cursor)
            set_parts = ["[Nombre] = ?", "[Precio] = ?", "[Ingredientes] = ?", "[Disponible] = ?", "[Stock] = ?"]
            values = [producto_vo.nombre, producto_vo.precio, producto_vo.ingredientes, self._normalize_yes_no(producto_vo.disponible), producto_vo.stock]
            if schema["category_column"]: #si existe una columna de categoria, se añade a la lista de columnas a actualizar y valores a actualizar
                set_parts.append(f"{self._quote_identifier(schema['category_column'])} = ?")
                values.append(producto_vo.categoria)
            elif producto_vo.categoria:
                raise ValueError("La base de datos actual no tiene columna de categoria en PRODUCTOS.")
            values.append(nombre_original) #se añade el nombre original al final de los valores, para usarlo en la cláusula WHERE
            cursor.execute(f"UPDATE PRODUCTOS SET {', '.join(set_parts)} WHERE [Nombre] = ?", values)
            self.conexion.commit()
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback()
            if self._is_constraint_error(exc):
                raise ValueError("No se pudo actualizar el producto. Revisa si el nombre ya existe o si los datos incumplen una restriccion.") from exc
            raise
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def eliminar(self, nombre_producto):
        """Elimina un producto de la base de datos identificado por su nombre."""
        cursor = self.getCursor()
        try:
            cursor.execute("DELETE FROM PRODUCTOS WHERE [Nombre] = ?", (nombre_producto,))
            self.conexion.commit()
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback()
            if self._is_constraint_error(exc):
                raise ValueError("No se puede eliminar el producto porque esta relacionado con otros registros. PARA QUE NO APAREZCA EN LA CARTA, MARCAR COMO NO DISPONIBLE :) ") from exc
            raise
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def describir(self):
        """Devuelve un diccionario con información sobre las columnas de la tabla PRODUCTOS, incluyendo si existe una columna de categoria."""
        cursor = self.getCursor()
        try:
            return self._get_schema_info(cursor)
        except Exception as exc:
            raise RuntimeError(f"No se pudo leer la estructura de PRODUCTOS: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def _get_schema_info(self, cursor):
        """Lee las columnas de la tabla PRODUCTOS y determina si existe una columna de categoria."""
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'PRODUCTOS'
            """
        )
        columns = {row[0] for row in cursor.fetchall()}
        return {"columns": columns, "category_column": self._find_existing_column(columns, self.CATEGORY_COLUMNS)}

    def _find_existing_column(self, columns, candidates):
        """Busca la primera columna que exista en el conjunto dado, o devuelve None si no se encuentra ninguna."""
        for candidate in candidates:
            if candidate in columns:
                return candidate
        return None

    def _category_select(self, schema):
        """Devuelve la parte de la consulta SQL para seleccionar la categoria, dependiendo de si existe una 
        columna de categoria en el esquema."""
        if schema["category_column"]:
            return f"{self._quote_identifier(schema['category_column'])} AS Categoria"
        return "CAST('' AS nvarchar(100)) AS Categoria"

    def _quote_identifier(self, name):
        """Devuelve el nombre de columna o tabla entre corchetes para evitar problemas con palabras reservadas o espacios."""
        return f"[{name}]"

    def _normalize_yes_no(self, value):
        """Convierte un valor booleano o similar a 'Y' o 'N' para almacenar en la base de datos."""
        text = str(value).strip().upper()
        return "Y" if text in ("Y", "SI", "S", "YES", "TRUE", "1") else "N"

    def _is_constraint_error(self, exc):
        """Determina si una excepción dada corresponde a un error de restricción o integridad,
        como violaciones de clave única o restricciones de integridad referencial."""
        text = str(exc).lower()
        return any(token in text for token in ("duplicate", "unique", "constraint", "violation", "integrity", "sqlstate=23000"))
