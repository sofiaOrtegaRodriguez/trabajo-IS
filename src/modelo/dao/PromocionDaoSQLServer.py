import pyodbc

from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.vo.PromocionVo import PromocionVo


class PromocionDaoSQLServer:
    def __init__(self):
        self._conexion = ConexionSQLServer.get_instance()

    def listar(self):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
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
            ConexionSQLServer.close(conn)

    def crear(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
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
            cursor.execute(
                """
                INSERT INTO PRODPROM (NombreProd, IDProm)
                VALUES (?, ?)
                """,
                (nombre_producto, id_promocion),
            )
            conn.commit()
            return id_promocion
        except pyodbc.IntegrityError as exc:
            if conn is not None:
                conn.rollback()
            raise ValueError("No se pudo crear la promocion. Revisa las fechas, el descuento o el producto elegido.") from exc
        except Exception:
            if conn is not None:
                conn.rollback()
            raise
        finally:
            ConexionSQLServer.close(conn)

    def eliminar(self, id_promocion):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PRODPROM WHERE IDProm = ?", (id_promocion,))
            cursor.execute("DELETE FROM PROMOCIONES WHERE IDProm = ?", (id_promocion,))
            conn.commit()
        except Exception:
            if conn is not None:
                conn.rollback()
            raise
        finally:
            ConexionSQLServer.close(conn)
