from datetime import date

import pyodbc

from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.vo.SesionVo import SesionVo
from src.modelo.vo.UsuariosVo import UsuariosVo


class UserDaoSQLServer:
    def __init__(self):
        self._conexion = ConexionSQLServer.get_instance()

    SQL_SELECT = """
        SELECT IdCli, Nombre, Correo, Puntos, FechaCuenta
        FROM CLIENTES
    """

    SQL_CHECK_LOGIN = """
        SELECT IdCli, Nombre, Correo, Puntos, FechaCuenta
        FROM CLIENTES
        WHERE Correo = ? AND Contrasena = ?
    """

    SQL_INSERT_CLIENTE = """
        INSERT INTO CLIENTES (Nombre, Correo, Contrasena, Puntos, FechaCuenta)
        VALUES (?, ?, ?, ?, ?)
    """

    def consultarLogin(self, login_vo):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_CHECK_LOGIN, (login_vo.nombre, login_vo.contrasena))
            row = cursor.fetchone()
            if row is None:
                return None
            return SesionVo(row.IdCli, row.Nombre, row.Correo, row.Puntos, row.FechaCuenta, "cliente")
        except Exception as exc:
            raise RuntimeError(f"No se pudo conectar a SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def select(self):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_SELECT)
            return [UsuariosVo(*row) for row in cursor.fetchall()]
        except Exception as exc:
            raise RuntimeError(f"No se pudo consultar SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def registrarCliente(self, nombre, correo, contrasena):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                self.SQL_INSERT_CLIENTE,
                (nombre, correo, contrasena, 0, date.today()),
            )
            conn.commit()
        except pyodbc.IntegrityError as exc:
            if conn is not None:
                conn.rollback()
            raise ValueError("Ya existe un cliente registrado con ese correo o nombre.") from exc
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            raise RuntimeError(f"No se pudo registrar el cliente en SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def actualizarPuntos(self, id_cliente, puntos):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE CLIENTES SET Puntos = Puntos + ? WHERE IdCli = ?",
                (int(puntos), int(id_cliente)),
            )
            conn.commit()
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            raise RuntimeError(f"No se pudieron actualizar los puntos del cliente: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)
