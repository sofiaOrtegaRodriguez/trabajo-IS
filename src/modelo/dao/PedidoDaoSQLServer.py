from datetime import datetime

from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.vo.PedidoVo import PedidoDetalleVo, PedidoVo


class PedidoDaoSQLServer:
    def __init__(self):
        self._conexion = ConexionSQLServer.get_instance()

    def crear(self, sesion, items, total):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()

            id_cliente = None if sesion.es_cajero else sesion.id_sesion
            id_cajero = sesion.id_sesion if sesion.es_cajero else None

            cursor.execute(
                """
                INSERT INTO PEDIDOS (PrecioTotal, Hora, Estado, IDCli, IDCaj)
                OUTPUT INSERTED.IDPed
                VALUES (?, ?, ?, ?, ?)
                """,
                (float(total), datetime.now(), "PAGADO", id_cliente, id_cajero),
            )
            row = cursor.fetchone()
            id_pedido = int(row[0])

            for item in items:
                cursor.execute(
                    """
                    INSERT INTO PRODPED (NombreProd, IDPed, Cantidad)
                    VALUES (?, ?, ?)
                    """,
                    (item["nombre"], id_pedido, int(item["cantidad"])),
                )

            conn.commit()
            return id_pedido
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            raise RuntimeError(f"No se pudo guardar el pedido en SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def listar(self, sesion):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()

            if sesion.es_cajero:
                cursor.execute(
                    """
                    SELECT p.IDPed, p.PrecioTotal, p.Hora, p.Estado, pp.NombreProd, pp.Cantidad, prod.Precio
                    FROM PEDIDOS p
                    LEFT JOIN PRODPED pp ON pp.IDPed = p.IDPed
                    LEFT JOIN PRODUCTOS prod ON prod.Nombre = pp.NombreProd
                    WHERE p.IDCaj IS NOT NULL
                    ORDER BY p.Hora DESC, p.IDPed DESC, pp.NombreProd
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT p.IDPed, p.PrecioTotal, p.Hora, p.Estado, pp.NombreProd, pp.Cantidad, prod.Precio
                    FROM PEDIDOS p
                    LEFT JOIN PRODPED pp ON pp.IDPed = p.IDPed
                    LEFT JOIN PRODUCTOS prod ON prod.Nombre = pp.NombreProd
                    WHERE p.IDCli = ?
                    ORDER BY p.Hora DESC, p.IDPed DESC, pp.NombreProd
                    """,
                    (sesion.id_sesion,),
                )

            pedidos = {}
            for row in cursor.fetchall():
                pedido = pedidos.get(row.IDPed)
                if pedido is None:
                    hora_value = row.Hora
                    if hasattr(hora_value, "strftime"):
                        fecha_text = hora_value.strftime("%d/%m/%Y")
                        hora_text = hora_value.strftime("%H:%M")
                    else:
                        fecha_text = str(hora_value)
                        hora_text = ""
                    pedido = PedidoVo(
                        row.IDPed,
                        fecha_text,
                        hora_text,
                        row.Estado,
                        [],
                        float(row.PrecioTotal),
                    )
                    pedidos[row.IDPed] = pedido

                if row.NombreProd is not None:
                    price = float(row.Precio or 0)
                    qty = int(row.Cantidad or 0)
                    pedido.productos.append(
                        PedidoDetalleVo(
                            row.NombreProd,
                            qty,
                            round(price * qty, 2),
                        )
                    )

            return list(pedidos.values())
        except Exception as exc:
            raise RuntimeError(f"No se pudo cargar el historial de pedidos: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)
