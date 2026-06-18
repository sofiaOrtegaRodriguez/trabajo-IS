from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer # clase base que gestiona la conexión con la bd
from src.modelo.vo.EmpleadoVo import EmpleadoVo # VO que representa los datos de un empleado
from src.modelo.vo.SesionVo import SesionVo # VO que representa la sesión del usuario logueado

# DAO que gestiona todas las operaciones de la tabla EMPLEADOS en la BD
# hereda de ConexionSQLServer para tener acceso a la conexión y al cursor

class EmpleadoDaoJDBC(ConexionSQLServer):

    # consulta SQL para comprobar el login: busca un empleado por su correo y contraseña
    # solamente permite empleados de esos 4 roles
    SQL_CHECK_LOGIN = """
        SELECT IDEmp, Emp_User, Emp_Correo, Emp_Tipo
        FROM EMPLEADOS
        WHERE Emp_Correo = ? 
          AND Emp_Contrasena = ?
          AND Emp_Tipo IN ('ADMINISTRADOR', 'GERENTE', 'COCINA', 'CAJERO')
    """


    # consulta SQL para listar solo los empleados gestionables (cajero y cocina)
    # loa ordena primero por cajeros y después por nombre alfabéticamente
    SQL_LIST = """
        SELECT IDEmp, Emp_SSN, Emp_User, Emp_Correo, Emp_Contrasena, Emp_Tipo
        FROM EMPLEADOS
        WHERE Emp_Tipo IN ('CAJERO', 'COCINA')
        ORDER BY CASE WHEN Emp_Tipo = 'CAJERO' THEN 0 ELSE 1 END, Emp_User
    """

    # consulta SQL para obtener el tipo de empleado concreto por su ID
    # se usa antes de acturlizar par saber qué rol tenía antes del cambio
    SQL_GET_TYPE = """
        SELECT Emp_Tipo
        FROM EMPLEADOS
        WHERE IDEmp = ?
    """

    # consulta SQL para insertar un nuevo empleado en la BD
    # OUTPUT INSERTED.IDEmp devuelve el id generado automáticamente tras el INSERT
    SQL_INSERT = """
        INSERT INTO EMPLEADOS (Emp_SSN, Emp_User, Emp_Correo, Emp_Contrasena, Emp_Tipo)
        OUTPUT INSERTED.IDEmp
        VALUES (?, ?, ?, ?, ?)
    """

    # consulta SQL para actualizar los datos de un empleado existente identificado por el ID
    SQL_UPDATE = """
        UPDATE EMPLEADOS
        SET Emp_SSN = ?, Emp_User = ?, Emp_Correo = ?, Emp_Contrasena = ?, Emp_Tipo = ?
        WHERE IDEmp = ?
    """

    # consulta SQL para eliminar un empleado por su ID
    SQL_DELETE = "DELETE FROM EMPLEADOS WHERE IDEmp = ?"

    # función que comprueba si un empleado existe en la BD con ese correo y contraseña
    # devuelve un SesionVo con su rol si el login es cprrecto, o None si no existe
    def consultarLogin(self, login_vo):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CHECK_LOGIN, (login_vo.correo, login_vo.contrasena))
            row = cursor.fetchone() # obtenemos solo la prinera fila (debería ser única)
            if row is None: # si no hay resultado, el login es incorrecto
                return None
            rol = str(row.Emp_Tipo).strip().lower() # convertimos el tipo a minus. para qie coincida con factoria rol
            return SesionVo(row.IDEmp, row.Emp_User, row.Emp_Correo, 0, None, rol) # construimos la sesión con 0 puntos, los empleados no tienen
        except Exception as exc:
            raise RuntimeError(f"No se pudo autenticar el empleado en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close() # cerramos el cursor siempre, haya error o no
            self.closeConnection() # cerramos la conexión con la BD siempre

    # función que devuelve la lista de empleados gestionables (cajero y cocina) como lista de EmpleadoVo
    def listar(self):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_LIST)
            return [
                EmpleadoVo(row.IDEmp, row.Emp_SSN, row.Emp_User, row.Emp_Correo, row.Emp_Contrasena, row.Emp_Tipo)
                for row in cursor.fetchall() # convertimos cada fila en un EmpleadoVo con comprensión de lista
            ]
        except Exception as exc:
            raise RuntimeError(f"No se pudo listar el personal en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función que inserta un nuevo empleado en la BD, solo puede ser cajero o cocina
    def crear(self, ssn, usuario, correo, contrasena, tipo):
        cursor = self.getCursor()
        tipo = str(tipo).strip().upper() # normalizamos el tipo a mayúsculas para comparar
        if tipo not in {"CAJERO", "COCINA"}: # solamente se pueden crear empleados de estos dos tipos
            raise ValueError("Solo se pueden gestionar empleados de tipo CAJERO o COCINA.")
        try:
            cursor.execute(self.SQL_INSERT, (ssn, usuario, correo, contrasena, tipo))
            row = cursor.fetchone()
            id_empleado = int(row[0]) # obtenemos el id generado automáticamente por el INSERT
            if tipo == "CAJERO":
                self._ensure_cashier_row(cursor, id_empleado) # si es cajero, también lo añadimos a la tabla CAJEROS
            self.conexion.commit() # confirmamos la transacción para guardar todos los cambios
            return id_empleado # devolvemos el id del nuevo empleado
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback() # si hay error deshacemos todos los cambios
            if self._is_constraint_error(exc):
                raise ValueError("Ya existe un empleado con ese correo, usuario o DNI.") from exc
            raise RuntimeError(f"No se pudo crear el empleado en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función que actualiza los datos de un empleado existente por su id
    # si cambia de cocina a cajero lo añade a cajeros, si cambia de cajero a cocina lo elimina de cajeros
    def actualizar(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        cursor = self.getCursor()
        tipo = str(tipo).strip().upper() # normalizamos el tipo a mayúsculas
        if tipo not in {"CAJERO", "COCINA"}: # solamente podemos gestionar cajero o cocina
            raise ValueError("Solo se pueden gestionar empleados de tipo CAJERO o COCINA.")
        try:
            cursor.execute(self.SQL_GET_TYPE, (int(id_empleado),))
            row = cursor.fetchone()
            if row is None: # si no existee el empleado, lanzamos un error claro
                raise ValueError("No existe el empleado que quieres modificar.")
            cursor.execute(self.SQL_UPDATE, (ssn, usuario, correo, contrasena, tipo, int(id_empleado))) # actualizamos sus datos
            if tipo == "CAJERO":
                self._ensure_cashier_row(cursor, int(id_empleado)) # si ahora es cajero, nos aseguramos de que esté en CAJEROS
            else:
                self._remove_cashier_row(cursor, int(id_empleado)) # si ya no es cajero, lo eliminamos de CAJEROS
            self.conexion.commit() # confirmamos todos los cambios
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback() # si hay error, deshacemos todos los cambios
            if self._is_constraint_error(exc):
                raise ValueError("Ya existe un empleado con ese correo, usuario o DNI.") from exc
            raise RuntimeError(f"No se pudo actualizar el empleado en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función que elimina un empleado de la BD por su id
    # primero lo elimina de CAJEROS si fuera cajero, y luego lo borra de EMPLEADOS
    def eliminar(self, id_empleado):
        cursor = self.getCursor()
        try:
            self._remove_cashier_row(cursor, int(id_empleado)) # borramos de CAJEROS primero para no violar la integridad referencial
            cursor.execute(self.SQL_DELETE, (int(id_empleado),)) # luego lo borramos de EMPLEADOS
            self.conexion.commit()
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback() # si hay error, deshacemos los cambios
            raise RuntimeError(f"No se pudo eliminar el empleado en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función auxiliar que inserta al empleado en la tabla CAJEROS solo si no existe ya
    # se llama al crear o actualizar un empleado de tipo CAJERO
    def _ensure_cashier_row(self, cursor, id_empleado):
        cursor.execute("SELECT 1 FROM CAJEROS WHERE ID_Cajero = ?", (int(id_empleado),))
        if cursor.fetchone() is None: # si no existe en CAJEROS, lo insertamos
            cursor.execute("INSERT INTO CAJEROS (ID_Cajero) VALUES (?)", (int(id_empleado),))


    # función auxiliar que elimina al empleado de la tabla CAJEROS si existe
    # se llama al eliminar un empleado o cuando un cajero cambiar a otro tipo
    def _remove_cashier_row(self, cursor, id_empleado):
        cursor.execute("DELETE FROM CAJEROS WHERE ID_Cajero = ?", (int(id_empleado),))


    # función auxiliar que detecta si un error de BD es por violación de restricción única (datos duplicados)
    # devuelve True si el mensajae de error contiene alguna palabra clave típica de este tipo de error
    def _is_constraint_error(self, exc):
        text = str(exc).lower() # lo cambiamos a minusc. para comparar bien
        return any(token in text for token in ("duplicate", "unique", "constraint", "violation", "integrity", "sqlstate=23000"))
