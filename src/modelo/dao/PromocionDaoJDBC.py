from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.dao.PromocionDao import PromocionDao
from src.modelo.vo.PromocionVo import PromocionVo


class PromocionDaoJDBC(PromocionDao, ConexionSQLServer):
    def listar(self):
        cursor = self.getCursor()
        try:
            cursor.execute(
                """
                SELECT p.IDProm, p.Descuento, p.FechaInicio, p.FechaFin, pp.NombreProd
                FROM PROMOCIONES p
                LEFT JOIN PRODPROM pp ON pp.IDProm = p.IDProm
                ORDER BY p.FechaInicio DESC, p.IDProm DESC, pp.NombreProd
                """
            )
            return [
                PromocionVo(row.IDProm, int(row.Descuento), row.FechaInicio, row.FechaFin, row.NombreProd or "")
                for row in cursor.fetchall()
            ]
        except Exception as exc:
            raise RuntimeError(f"No se pudieron cargar las promociones: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def crear(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        cursor = self.getCursor()
        try:
            cursor.execute(
                """
                INSERT INTO PROMOCIONES (Descuento, FechaInicio, FechaFin)
                OUTPUT INSERTED.IDProm
                VALUES (?, ?, ?)
                """,
                (descuento, fecha_inicio, fecha_fin),
            )
            row = cursor.fetchone()
            id_promocion = int(row[0])
            cursor.execute("INSERT INTO PRODPROM (NombreProd, IDProm) VALUES (?, ?)", (nombre_producto, id_promocion))
            self.conexion.commit()
            return id_promocion
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback()
            if self._is_constraint_error(exc):
                raise ValueError("No se pudo crear la promocion. Revisa las fechas, el descuento o el producto elegido.") from exc
            raise RuntimeError(f"No se pudo crear la promocion: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def eliminar(self, id_promocion):
        cursor = self.getCursor()
        try:
            cursor.execute("DELETE FROM PRODPROM WHERE IDProm = ?", (id_promocion,))
            cursor.execute("DELETE FROM PROMOCIONES WHERE IDProm = ?", (id_promocion,))
            self.conexion.commit()
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback()
            raise RuntimeError(f"No se pudo eliminar la promocion: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def _is_constraint_error(self, exc):
        text = str(exc).lower()
        return any(token in text for token in ("duplicate", "unique", "constraint", "violation", "integrity", "sqlstate=23000"))
