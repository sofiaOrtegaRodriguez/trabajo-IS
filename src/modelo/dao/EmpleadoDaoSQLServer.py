import pyodbc

from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.vo.EmpleadoVo import EmpleadoVo
from src.modelo.vo.SesionVo import SesionVo


class EmpleadoDaoSQLServer:
    SQL_CHECK_LOGIN = """
        SELECT e.IDEmp, e.Emp_User, e.Emp_Correo, e.Emp_Tipo
        FROM EMPLEADOS e
        LEFT JOIN CAJEROS c ON c.ID_Cajero = e.IDEmp
        WHERE e.Emp_Correo = ? AND e.Emp_Contrasena = ?
          AND (
              e.Emp_Tipo = 'ADMINISTRADOR'
              OR e.Emp_Tipo = 'GERENTE'
              OR (e.Emp_Tipo = 'CAJERO' AND c.ID_Cajero IS NOT NULL)
          )
    """

    SQL_LIST = """
        SELECT IDEmp, Emp_SSN, Emp_User, Emp_Correo, Emp_Contrasena, Emp_Tipo
        FROM EMPLEADOS
        WHERE Emp_Tipo IN ('CAJERO', 'COCINA')
        ORDER BY CASE WHEN Emp_Tipo = 'CAJERO' THEN 0 ELSE 1 END, Emp_User
    """

    SQL_GET_TYPE = """
        SELECT Emp_Tipo
        FROM EMPLEADOS
        WHERE IDEmp = ?
    """

    SQL_INSERT = """
        INSERT INTO EMPLEADOS (Emp_SSN, Emp_User, Emp_Correo, Emp_Contrasena, Emp_Tipo)
        OUTPUT INSERTED.IDEmp
        VALUES (?, ?, ?, ?, ?)
    """

    SQL_UPDATE = """
        UPDATE EMPLEADOS
        SET Emp_SSN = ?, Emp_User = ?, Emp_Correo = ?, Emp_Contrasena = ?, Emp_Tipo = ?
        WHERE IDEmp = ?
    """

    SQL_DELETE = "DELETE FROM EMPLEADOS WHERE IDEmp = ?"

    def __init__(self):
        self._conexion = ConexionSQLServer.get_instance()

    def consultarLogin(self, login_vo):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_CHECK_LOGIN, (login_vo.nombre, login_vo.contrasena))
            row = cursor.fetchone()
            if row is None:
                return None
            nombre = row.Emp_User or row.Emp_Correo
            if row.Emp_Tipo == "ADMINISTRADOR":
                rol = "administrador"
            elif row.Emp_Tipo == "GERENTE":
                rol = "gerente"
            else:
                rol = "cajero"
            return SesionVo(row.IDEmp, nombre, row.Emp_Correo, 0, None, rol)
        except Exception as exc:
            raise RuntimeError(f"No se pudo autenticar el empleado en SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def listar(self):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_LIST)
            return [
                EmpleadoVo(
                    row.IDEmp,
                    row.Emp_SSN,
                    row.Emp_User,
                    row.Emp_Correo,
                    row.Emp_Contrasena,
                    row.Emp_Tipo,
                )
                for row in cursor.fetchall()
            ]
        except Exception as exc:
            raise RuntimeError(f"No se pudo listar el personal en SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def crear(self, ssn, usuario, correo, contrasena, tipo):
        conn = None
        tipo = str(tipo).strip().upper()
        if tipo not in {"CAJERO", "COCINA"}:
            raise ValueError("Solo se pueden gestionar empleados de tipo CAJERO o COCINA.")
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_INSERT, (ssn, usuario, correo, contrasena, tipo))
            row = cursor.fetchone()
            id_empleado = int(row[0])
            if tipo == "CAJERO":
                self._ensure_cashier_row(cursor, id_empleado)
            conn.commit()
            return id_empleado
        except pyodbc.IntegrityError as exc:
            if conn is not None:
                conn.rollback()
            raise ValueError("Ya existe un empleado con ese correo, usuario o DNI.") from exc
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            raise RuntimeError(f"No se pudo crear el empleado en SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def actualizar(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        conn = None
        tipo = str(tipo).strip().upper()
        if tipo not in {"CAJERO", "COCINA"}:
            raise ValueError("Solo se pueden gestionar empleados de tipo CAJERO o COCINA.")
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_GET_TYPE, (int(id_empleado),))
            row = cursor.fetchone()
            if row is None:
                raise ValueError("No existe el empleado que quieres modificar.")
            tipo_anterior = str(row.Emp_Tipo).upper()

            cursor.execute(
                self.SQL_UPDATE,
                (ssn, usuario, correo, contrasena, tipo, int(id_empleado)),
            )

            if tipo == "CAJERO":
                self._ensure_cashier_row(cursor, int(id_empleado))
            else:
                self._remove_cashier_row(cursor, int(id_empleado))

            conn.commit()
        except pyodbc.IntegrityError as exc:
            if conn is not None:
                conn.rollback()
            raise ValueError("Ya existe un empleado con ese correo, usuario o DNI.") from exc
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            raise RuntimeError(f"No se pudo actualizar el empleado en SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def eliminar(self, id_empleado):
        conn = None
        try:
            conn = self._conexion.get_connection()
            cursor = conn.cursor()
            self._remove_cashier_row(cursor, int(id_empleado))
            cursor.execute(self.SQL_DELETE, (int(id_empleado),))
            conn.commit()
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            raise RuntimeError(f"No se pudo eliminar el empleado en SQL Server: {exc}") from exc
        finally:
            ConexionSQLServer.close(conn)

    def _ensure_cashier_row(self, cursor, id_empleado):
        cursor.execute("SELECT 1 FROM CAJEROS WHERE ID_Cajero = ?", (int(id_empleado),))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO CAJEROS (ID_Cajero) VALUES (?)", (int(id_empleado),))

    def _remove_cashier_row(self, cursor, id_empleado):
        cursor.execute("DELETE FROM CAJEROS WHERE ID_Cajero = ?", (int(id_empleado),))
