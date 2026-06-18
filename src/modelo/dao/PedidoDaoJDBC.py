# DAO que gestiona todas las operaciones de la tabla PEDIDOS en la BD
# hereda de ConexionSQLServer para tener acceso a la conexión y al cursor


from datetime import datetime # para obtener la fecha y hora actual al crear un pedido

from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer # clase que gestiona la conexión con la BD
from src.modelo.vo.PedidoVo import PedidoDetalleVo, PedidoVo # VOs que representan un pedido y sus líneas de detalle


class PedidoDaoJDBC(ConexionSQLServer):

    # función auxiliar que deshace la transacción actual si la conexión no está en modo autocommit
    # se llama cuando ocurre un error para no dejar la BD en un estado inconsciente
    def _rollback_if_needed(self):
        if self.conexion is None: # si no hay conexión no hay nada que deshacer
            return
        try:
            is_autocommit = self.conexion.getAutoCommit() # intentamos obtener el modo de la conexión normal
        except Exception:
            try:
                is_autocommit = self.conexion.jconn.getAutoCommit() # si falla, lo intentamos con la conexión JDBC interna
            except Exception:
                is_autocommit = False # si ambos fallan, asumimos que no es autocommit y hacemos rollback
        if not is_autocommit:
            self.conexion.rollback() # deshacemos los cambios si no estamos en autocommit

    # función que inserta u nuevo pedido en la BD con todos sus productos
    # devuelve el id del pedido creado
    def crear(self, sesion, items, total):
        cursor = self.getCursor()
        try:
            # si el pedido lo hace el cajero, el id del cliente es none y se guarda guarda el id del cajero
            # si lo hace el cliente se guarda el id del cliente, y el de cjaero es None
            id_cliente = None if sesion.es_cajero else sesion.id_sesion
            id_cajero = sesion.id_sesion if sesion.es_cajero else None
            hora_pedido = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # guardamos la fecha y hora exacta del pedido
            cursor.execute(
                """
                INSERT INTO PEDIDOS (PrecioTotal, Hora, Estado, IDCli, IDCaj)
                OUTPUT INSERTED.IDPed
                VALUES (?, ?, ?, ?, ?)
                """,
                (float(total), hora_pedido, "PENDIENTE", id_cliente, id_cajero),
                # todo pedido nuevo empieza con estado PENDIENTE
            )
            row = cursor.fetchone()
            id_pedido = int(row[0]) # obtenemos el id generado automáticamente por el INSERT
            for item in items:
                # insertamos cada producto del pedido en la tabla PROPED (productos del pedido)
                cursor.execute(
                    """
                    INSERT INTO PRODPED (NombreProd, IDPed, Cantidad)
                    VALUES (?, ?, ?)
                    """,
                    (item["nombre"], id_pedido, int(item["cantidad"])),
                )
                cursor.execute(
                    """
                    UPDATE PRODUCTOS SET Stock = Stock - ? WHERE Nombre = ?
                    """,
                    (int(item["cantidad"]), item["nombre"])
                )
            self.conexion.commit() # confirmamos todos los cambios (pedido + productos) a la vez
            return id_pedido # devolvemos el id del pedido
        except Exception as exc:
            self._rollback_if_needed() # si algo falla, deshacemos todos los cambios
            raise RuntimeError(f"No se pudo guardar el pedido en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función que devuelve el historial de pedidos según el rol de la sesión:
    # si es cajero devuelve todos los pedidos hechos por el cajero, si es cliente devuelve solo los suyos
    def listar(self, sesion):
        cursor = self.getCursor()
        try:
            if sesion.es_cajero:
                # el cajero ve todos los pedidos que pasaron por caja (IDCaj no es NULL)
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
                # el cliente solo ve sus propios pedidos filtrados por su id
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
            pedidos = {} # diccionario para agrupar las filas por id del pedido (evita duplicados)
            for row in cursor.fetchall():
                pedido = pedidos.get(row.IDPed) # buscamos si ya hemos procesado este pedido antes
                if pedido is None:
                    # si es la primera vez que vemos este pedido, lo creamos
                    hora_value = row.Hora
                    if hasattr(hora_value, "strftime"):
                        # si la hora es un objeto datetime, lo formateamos a texto legible
                        fecha_text = hora_value.strftime("%d/%m/%Y")
                        hora_text = hora_value.strftime("%H:%M")
                    else:
                        # si ya viene como texto, lo usamos directamente
                        fecha_text = str(hora_value)
                        hora_text = ""
                    pedido = PedidoVo(row.IDPed, fecha_text, hora_text, row.Estado, [], float(row.PrecioTotal))
                    pedidos[row.IDPed] = pedido # lo guardamos en el diccionrio
                if row.NombreProd is not None:
                    # si la fila tiene producto, calculamos su subtotal y lo añadimos al pedido
                    price = float(row.Precio or 0)
                    qty = int(row.Cantidad or 0)
                    pedido.productos.append(PedidoDetalleVo(row.NombreProd, qty, round(price * qty, 2)))
            return list(pedidos.values()) # devolvemos la lista de pedidos ya con sus productos
        except Exception as exc:
            raise RuntimeError(f"No se pudo cargar el historial de pedidos: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función que devuelve todos los pedidos del día actual en tiempo real (para cocina y cajero)
    # no filtra por usuario, devuelve todos los pedidos de hoy sin importar quién los hizo
    def listarTiempoReal(self):
        cursor = self.getCursor()
        try:
            cursor.execute(
                """
                SELECT p.IDPed, p.PrecioTotal, p.Hora, p.Estado, p.IDCli, pp.NombreProd, pp.Cantidad
                FROM PEDIDOS p
                LEFT JOIN PRODPED pp ON pp.IDPed = p.IDPed
                WHERE CAST(Hora AS DATE) = CAST(GETDATE() AS DATE)
                ORDER BY p.Hora DESC, p.IDPed DESC, pp.NombreProd
                """
                # CAST(Hora AS DATE) = CAST(GETDATE() AS DATE) filtra solo los pedidos de hoy
            )
            pedidos = {} # diccionario para agrupar las filas por id de pedido
            for row in cursor.fetchall():
                pedido = pedidos.get(row.IDPed)
                if pedido is None:
                    # si es la primera vez que vemos este pedido, lo creamos
                    hora_value = row.Hora
                    usuario = row.IDCli if row.IDCli is not None else "Cajero" # si no hay cliente, entonces el pedido fue hecho por un cajero
                    if hasattr(hora_value, "strftime"):
                        fecha_text = hora_value.strftime("%d/%m/%Y")
                        hora_text = hora_value.strftime("%H:%M")
                    else:
                        fecha_text = str(hora_value)
                        hora_text = ""
                    pedido = PedidoVo(row.IDPed, fecha_text, hora_text, row.Estado, [], float(row.PrecioTotal), usuario)
                    pedidos[row.IDPed] = pedido
                if row.NombreProd is not None:
                    qty = int(row.Cantidad or 0)
                    pedido.productos.append(PedidoDetalleVo(row.NombreProd, qty, None))
                    # el subtotal es None porque en tiempo real no se necesita el precio, solo el nombre y cantidad
            return list(pedidos.values()) # devolvemos la lista de pedidos de hoy
        except Exception as exc:
            raise RuntimeError(f"No se pudieron cargar los pedidos: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función que actualiza el estadod de un pedido en laBD
    # recibe un PedidoVo con el id  y ek nuevo estado ya asignado
    def modificarEstado(self, pedido):
        cursor = self.getCursor()
        try:
            cursor.execute("UPDATE PEDIDOS SET Estado = ? WHERE IDPed = ?", (pedido.estado, pedido.id))
            self.conexion.commit() # confirmamos el cambio de estado
            return 1 # devolvemos 1 para indicar que la operación fue exitosa
        except Exception as exc:
            self._rollback_if_needed() # si falla, deshacemos el cambio
            raise RuntimeError(f"No se pudo modificar el estado del pedido en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()
