# DAO que gestiona todas las operaciones de la tabla CLIENTES en la BD
# hereda de ConexionSQLServer para tener acceso a la conexión y al cursor

from datetime import date # para obtener la fecha actual al registrar un cliente


from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer # clase base que gestiona la conexión con la BD
from src.modelo.vo.SesionVo import SesionVo # VO que representa la sesión del user logueado

class UserDaoJDBC(ConexionSQLServer):

    # consulta SQL para obtener todos los clientes de la BD
    SQL_SELECT = """
        SELECT IdCli, Nombre, Correo, Puntos, FechaCuenta
        FROM CLIENTES
    """

    # consulta SQL para comprobar el login: busca un cliente por su correo y contraseña
    SQL_CHECK_LOGIN = """
        SELECT IdCli, Nombre, Correo, Puntos, FechaCuenta
        FROM CLIENTES
        WHERE Correo = ? AND Contrasena = ?
    """

    # consulta SQL para insertar un nuevo cliente en la BD con sus datos
    SQL_INSERT_CLIENTE = """
        INSERT INTO CLIENTES (Nombre, Correo, Contrasena, Puntos, FechaCuenta)
        VALUES (?, ?, ?, ?, ?)
    """

    # función que nos devuelve todos los clientes de la BD como lista de SesionVo
    def select(self):
        cursor = self.getCursor() # obtenemos el cursor para ejecutar consultas
        usuarios = [] # lista donde iremos gurdando los usuarios
        try:
            cursor.execute(self.SQL_SELECT) # ejecutamos la consulta SELECT
            for row in cursor.fetchall(): # recorremos todas las filas devueltas
                usuarios.append(SesionVo(*row)) # convertimos cada fila en un SesionVo y lo añadimos a la lista
        except Exception as exc:
            raise RuntimeError(f"No se pudo consultar SQL Server: {exc}") from exc # mensaje de error en caso de que no se pueda consultar
        finally:
            if cursor is not None: # si el cursor no es None
                cursor.close() # cerramos el cursor siempre, haya error o no
            self.closeConnection() # cerramos la conexión con la BD siempre
        return usuarios # devolvemos la lista de usuarios

    # función que comprueba si un cliente existe en la BD con ese correo y contraseña
    # devuelve un SesionVo si el login es correcto, o None si no existe 
    def consultarLogin(self, login_vo):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CHECK_LOGIN, (login_vo.correo, login_vo.contrasena)) # buscamos por correo y contraseña
            row = cursor.fetchone() # obtenemos solo la primera fila (debería ser única)
            if row is None: # si no hay resultado, el login es incorrecto
                return None
            # si hay resultado, construimos y devolvemos la sesión del cliente con rol "cliente"
            return SesionVo(row.IdCli, row.Nombre, row.Correo, row.Puntos, row.FechaCuenta, "cliente")
        except Exception as exc:
            raise RuntimeError(f"No se pudo conectar a SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()


    # función que inserta un nuevo cliente en la BD con los datos del formulario de registro
    def registrarCliente(self, registroVo):
        cursor = self.getCursor()
        fecha_actual_texto = date.today().isoformat() # obtenemos la fecha de hoy en formato text (YYYY-MM-DD)
        try:
            cursor.execute(
                self.SQL_INSERT_CLIENTE,
                (registroVo.nombre, registroVo.correo, registroVo.contrasena, 0, fecha_actual_texto),
                # se inserta con 0 puntos iniciales y la fecha de hoy como fecha de creación de cuenta
            )
            self.conexion.commit() # confirmamos la transacción para que el INSERT se guarde en la BD
        except Exception as exc:
            if self._is_constraint_error(exc): # si el error es por un correo duplicado, lanzamos un error más claro
                raise ValueError("Ya existe un cliente registrado con ese correo.") from exc
            raise RuntimeError(f"No se pudo registrar el cliente en SQL Server: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función que suma o resta puntos a un cliente en la BD (puntos positivos suman, negativos restan)
    def actualizarPuntos(self, id_cliente, puntos):
        cursor = self.getCursor()
        try:
            cursor.execute(
                "UPDATE CLIENTES SET Puntos = Puntos + ? WHERE IdCli = ?", # se ponen los puntos al cliente cuyo ID coincida con el pasado
                (int(puntos), int(id_cliente)), # sumamos los puntos al valor actual (o restamos, depende)
            )
            self.conexion.commit() # confirmamos la transacción para que el UPDATE se guarde en la BD
        except Exception as exc:
            if self.conexion is not None:
                self.conexion.rollback() # si hay error, deshaemos el UPDATE para no dejar la BD en un estado inconsistente
            raise RuntimeError(f"No se pudieron actualizar los puntos del cliente: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    # función auxiliar que detecta si un error de BD es por violación de restricción única (correo duplicado)
    # devuelve TRUE si el mensaje de error contiene alguna de las palabras clave típicas de este tipo de error
    def _is_constraint_error(self, exc):
        text = str(exc).lower() # convertimos el mensaje a minúsculas para comprar sin  importar como esta escrito
        return any(token in text for token in ("duplicate", "unique", "constraint", "violation", "integrity", "sqlstate=23000"))
