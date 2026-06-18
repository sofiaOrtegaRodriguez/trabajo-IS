#se utilizan para trabajar con fechas
from datetime import date, datetime

#clase que gestiona la conexión con SQL Server
from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer

#objeto que representa una promoción
from src.modelo.vo.PromocionVo import PromocionVo


#DAO encargado de acceder a los datos de promociones en la BD
class PromocionDaoJDBC(ConexionSQLServer):

    #obtiene todas las promociones almacenadas en la BD
    def listar(self):

        #obtiene un cursor para ejecutar consultas SQL
        cursor = self.getCursor()

        try:

            #consulta que recupera las promociones y el producto asociado
            cursor.execute(
                """
                SELECT p.IDProm, p.Descuento, p.FechaInicio, p.FechaFin, pp.NombreProd
                FROM PROMOCIONES p
                LEFT JOIN PRODPROM pp ON pp.IDProm = p.IDProm
                ORDER BY p.FechaInicio DESC, p.IDProm DESC, pp.NombreProd
                """
            )

            #convierte cada fila obtenida en un objeto PromocionVo
            return [
                PromocionVo(
                    row.IDProm,
                    int(row.Descuento),
                    self._coerce_date(row.FechaInicio),
                    self._coerce_date(row.FechaFin),
                    row.NombreProd or "",
                )
                for row in cursor.fetchall()
            ]

        except Exception as exc:

            #si ocurre un error se lanza una excepción más descriptiva
            raise RuntimeError(
                f"No se pudieron cargar las promociones: {exc}"
            ) from exc

        finally:
            
            #cierra el cursor si existe
            if cursor is not None:
                cursor.close()

            #cierra la conexión con la BD
            self.closeConnection()

    #crea una nueva promoción en la BD
    def crear(self, descuento, fecha_inicio, fecha_fin, nombre_producto):

        #obtiene un cursor para ejecutar sentencias SQL
        cursor = self.getCursor()

        try:

            #inserta la promoción en la tabla PROMOCIONES
            cursor.execute(
                """
                INSERT INTO PROMOCIONES (Descuento, FechaInicio, FechaFin)
                OUTPUT INSERTED.IDProm
                VALUES (?, ?, ?)
                """,
                (descuento, fecha_inicio, fecha_fin),
            )

            #recupera el ID generado automáticamente
            row = cursor.fetchone()

            id_promocion = int(row[0])

            #relaciona la promoción con el producto seleccionado
            cursor.execute(
                "INSERT INTO PRODPROM (NombreProd, IDProm) VALUES (?, ?)",
                (nombre_producto, id_promocion)
            )

            #guarda definitivamente los cambios en la BD
            self.conexion.commit()

            #devuelve el id de la promoción creada
            return id_promocion

        except Exception as exc:

            #si ocurre un error se deshacen todos los cambios
            if self.conexion is not None:
                self.conexion.rollback()

            #comprueba si el error es debido a restricciones de la BD
            if self._is_constraint_error(exc):

                raise ValueError(
                    "No se pudo crear la promocion. Revisa las fechas, el descuento o el producto elegido."
                ) from exc

            #cualquier otro error se informa con un mensaje genérico
            raise RuntimeError(
                f"No se pudo crear la promocion: {exc}"
            ) from exc

        finally:

            #cierra el cursor si existe
            if cursor is not None:
                cursor.close()

            #cierra la conexión
            self.closeConnection()

    #elimina una promoción existente
    def eliminar(self, id_promocion):

        #obtiene un cursor para ejecutar consultas
        cursor = self.getCursor()

        try:

            #primero elimina la relación producto-promoción
            cursor.execute(
                "DELETE FROM PRODPROM WHERE IDProm = ?",
                (id_promocion,)
            )

            #después elimina la promoción principal
            cursor.execute(
                "DELETE FROM PROMOCIONES WHERE IDProm = ?",
                (id_promocion,)
            )

            #confirma los cambios
            self.conexion.commit()

        except Exception as exc:

            #si ocurre un error se cancelan los cambios
            if self.conexion is not None:
                self.conexion.rollback()

            raise RuntimeError(
                f"No se pudo eliminar la promocion: {exc}"
            ) from exc

        finally:

            #libera el cursor
            if cursor is not None:
                cursor.close()

            #cierra la conexión
            self.closeConnection()

    #comprueba si una excepción está relacionada con restricciones SQL
    def _is_constraint_error(self, exc):

        #convierte el mensaje a minúsculas para facilitar la búsqueda
        text = str(exc).lower()

        #busca palabras típicas de errores de integridad
        return any(
            token in text
            for token in (
                "duplicate",
                "unique",
                "constraint",
                "violation",
                "integrity",
                "sqlstate=23000",
            )
        )

    #convierte diferentes formatos de fecha al tipo date
    def _coerce_date(self, value):

        #si ya es una fecha válida se devuelve directamente
        if isinstance(value, date) and not isinstance(value, datetime):
            return value

        #si es datetime se extrae solamente la fecha
        if isinstance(value, datetime):
            return value.date()

        #si viene como texto se intenta convertir
        if isinstance(value, str):

            #formatos admitidos
            for fmt in (
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%Y-%m-%d %H:%M:%S",
            ):

                try:

                    #intenta convertir el texto a fecha
                    return datetime.strptime(
                        value,
                        fmt
                    ).date()

                except ValueError:

                    #si falla prueba con el siguiente formato
                    continue

        #si no se puede convertir devuelve el valor original
        return value