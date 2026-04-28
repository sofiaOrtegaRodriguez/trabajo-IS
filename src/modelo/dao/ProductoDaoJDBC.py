from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.dao.ProductoDao import ProductoDao
from src.modelo.vo.ProductoVo import ProductoVo


class ProductoDaoJDBC(ProductoDao, ConexionSQLServer):
    BASE_COLUMNS = ("Nombre", "Precio", "Ingredientes", "Disponible", "Stock")
    CATEGORY_COLUMNS = ("Categorias", "Categoria")

    def listar(self):
        cursor = self.getCursor()
        try:
            schema = self._get_schema_info(cursor)
            select_parts = ["[Nombre]", "[Precio]", "[Ingredientes]", "[Disponible]", "[Stock]", self._category_select(schema)]
            cursor.execute(
                f"""
                SELECT {", ".join(select_parts)}
                FROM PRODUCTOS
                ORDER BY Nombre
                """
            )
            return [
                ProductoVo(row.Nombre, float(row.Precio), row.Ingredientes, row.Disponible, int(row.Stock), getattr(row, "Categoria", "") or "")
                for row in cursor.fetchall()
            ]
        except Exception as exc:
            raise RuntimeError(f"No se pudieron cargar los productos: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def crear(self, producto_vo):
        cursor = self.getCursor()
        try:
            schema = self._get_schema_info(cursor)
            columns = list(self.BASE_COLUMNS)
            values = [producto_vo.nombre, producto_vo.precio, producto_vo.ingredientes, self._normalize_yes_no(producto_vo.disponible), producto_vo.stock]
            if schema["category_column"]:
                columns.append(schema["category_column"])
                values.append(producto_vo.categoria)
            elif producto_vo.categoria:
                raise ValueError("La base de datos actual no tiene columna de categoria en PRODUCTOS.")
            placeholders = ", ".join("?" for _ in columns)
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
        cursor = self.getCursor()
        try:
            schema = self._get_schema_info(cursor)
            set_parts = ["[Nombre] = ?", "[Precio] = ?", "[Ingredientes] = ?", "[Disponible] = ?", "[Stock] = ?"]
            values = [producto_vo.nombre, producto_vo.precio, producto_vo.ingredientes, self._normalize_yes_no(producto_vo.disponible), producto_vo.stock]
            if schema["category_column"]:
                set_parts.append(f"{self._quote_identifier(schema['category_column'])} = ?")
                values.append(producto_vo.categoria)
            elif producto_vo.categoria:
                raise ValueError("La base de datos actual no tiene columna de categoria en PRODUCTOS.")
            values.append(nombre_original)
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
        cursor = self.getCursor()
        try:
            cursor.execute("DELETE FROM PRODUCTOS WHERE [Nombre] = ?", (nombre_producto,))
            self.conexion.commit()
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback()
            if self._is_constraint_error(exc):
                raise ValueError("No se puede eliminar el producto porque esta relacionado con otros registros.") from exc
            raise
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def describir(self):
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
        for candidate in candidates:
            if candidate in columns:
                return candidate
        return None

    def _category_select(self, schema):
        if schema["category_column"]:
            return f"{self._quote_identifier(schema['category_column'])} AS Categoria"
        return "CAST('' AS nvarchar(100)) AS Categoria"

    def _quote_identifier(self, name):
        return f"[{name}]"

    def _normalize_yes_no(self, value):
        text = str(value).strip().upper()
        return "Y" if text in ("Y", "SI", "S", "YES", "TRUE", "1") else "N"

    def _is_constraint_error(self, exc):
        text = str(exc).lower()
        return any(token in text for token in ("duplicate", "unique", "constraint", "violation", "integrity", "sqlstate=23000"))
