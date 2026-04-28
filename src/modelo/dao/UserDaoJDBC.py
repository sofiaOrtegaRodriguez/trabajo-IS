from datetime import date

from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.dao.UserDao import UserDao
from src.modelo.vo.SesionVo import SesionVo
from src.modelo.vo.UsuariosVo import UsuariosVo


class UserDaoJDBC(UserDao, ConexionSQLServer):
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

    def select(self):
        cursor = self.getCursor()
        usuarios = []
        try:
            cursor.execute(self.SQL_SELECT)
            for row in cursor.fetchall():
                usuarios.append(UsuariosVo(*row))
        except Exception as exc:
            raise RuntimeError(f"No se pudo consultar SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()
        return usuarios

    def consultarLogin(self, login_vo):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CHECK_LOGIN, (login_vo.nombre, login_vo.contrasena))
            row = cursor.fetchone()
            if row is None:
                return None
            return SesionVo(row.IdCli, row.Nombre, row.Correo, row.Puntos, row.FechaCuenta, "cliente")
        except Exception as exc:
            raise RuntimeError(f"No se pudo conectar a SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def registrarCliente(self, nombre, correo, contrasena):
        cursor = self.getCursor()
        try:
            cursor.execute(
                self.SQL_INSERT_CLIENTE,
                (nombre, correo, contrasena, 0, date.today()),
            )
            self.conexion.commit()
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback()
            if self._is_constraint_error(exc):
                raise ValueError("Ya existe un cliente registrado con ese correo o nombre.") from exc
            raise RuntimeError(f"No se pudo registrar el cliente en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def actualizarPuntos(self, id_cliente, puntos):
        cursor = self.getCursor()
        try:
            cursor.execute(
                "UPDATE CLIENTES SET Puntos = Puntos + ? WHERE IdCli = ?",
                (int(puntos), int(id_cliente)),
            )
            self.conexion.commit()
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback()
            raise RuntimeError(f"No se pudieron actualizar los puntos del cliente: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def _is_constraint_error(self, exc):
        text = str(exc).lower()
        return any(token in text for token in ("duplicate", "unique", "constraint", "violation", "integrity", "sqlstate=23000"))
