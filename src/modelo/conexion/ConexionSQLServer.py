import os
from pathlib import Path
import traceback

try:
    import jaydebeapi
except ModuleNotFoundError as exc:  # pragma: no cover - runtime dependency only
    print("Error: No se pudo importar jaydebeapi. Asegúrate de tener la dependencia JDBC para Python instalada.")
    jaydebeapi = None
    _JDBC_IMPORT_ERROR = exc
else:
    _JDBC_IMPORT_ERROR = None


class JdbcRow:
    def __init__(self, columns, values):
        self._columns = tuple(columns)
        self._values = tuple(values)
        self._index = {column: idx for idx, column in enumerate(self._columns)}

    def __getattr__(self, name):
        if name in self._index:
            return self._values[self._index[name]]
        raise AttributeError(name)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return self._values[self._index[key]]

    def __iter__(self):
        return iter(self._values)


class JdbcCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        if params is None:
            self._cursor.execute(sql)
        else:
            self._cursor.execute(sql, params)
        return self

    def fetchone(self):
        return self._wrap_row(self._cursor.fetchone())

    def fetchall(self):
        return [self._wrap_row(row) for row in self._cursor.fetchall()]

    def close(self):
        self._cursor.close()

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def _wrap_row(self, row):
        if row is None or isinstance(row, JdbcRow):
            return row
        description = getattr(self._cursor, "description", None)
        if not description:
            return row
        columns = [column[0] for column in description]
        return JdbcRow(columns, row)


class ConexionSQLServer:
    """
    Conexión JDBC para SQL Server, siguiendo el patrón del ejemplo:
    - la conexión se crea al construir el objeto
    - getCursor() devuelve el cursor
    - closeConnection() cierra la conexión
    """

    _instance = None
    host = os.getenv("SUSHULE_DB_SERVER", r"127.0.0.1")
    database = os.getenv("SUSHULE_DB_NAME", "SushUle")
    user = os.getenv("SUSHULE_DB_USER", "app_user")
    password = os.getenv("SUSHULE_DB_PASSWORD", "Admin123")
    jdbc_driver = os.getenv("SUSHULE_JDBC_DRIVER", "com.microsoft.sqlserver.jdbc.SQLServerDriver")
    jar_file = os.getenv(
        "SUSHULE_JDBC_JAR",
        str(Path(__file__).resolve().parents[3] / "lib" / "mssql-jdbc-13.4.0.jre8.jar"),
    )
    encrypt = os.getenv("SUSHULE_JDBC_ENCRYPT", "true")
    trust_server_certificate = os.getenv("SUSHULE_JDBC_TRUST_CERT", "true")
    integrated_security = os.getenv("SUSHULE_JDBC_INTEGRATED", "yes").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "si",
    }


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host=None, database=None, user=None, password=None):
        if getattr(self, "_initialized", False):
            return
        self._host = host if host is not None else self.host
        self._database = database if database is not None else self.database
        self._user = user if user is not None else self.user
        self._password = password if password is not None else self.password
        self.conexion = self.createConnection()
        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()

    def createConnection(self):
        try:
            print(f"Intentando conectar a {self._host}...")
            if jaydebeapi is None:
                raise RuntimeError(
                    "No se pudo importar jaydebeapi. Instala la dependencia JDBC para Python."
                ) from _JDBC_IMPORT_ERROR

            if not os.path.exists(self.jar_file):
                raise FileNotFoundError(
                    f"No se encontro el driver JDBC de SQL Server en: {self.jar_file}"
                )

            jdbc_url = (
                f"jdbc:sqlserver://{self._host}:1433;"
                f"databaseName={self._database};"
                f"encrypt={self.encrypt};"
                f"trustServerCertificate={self.trust_server_certificate};"
            )
            if self.integrated_security and not self._user and not self._password:
                jdbc_url += ";integratedSecurity=true"

            credentials = [self._user, self._password] if self._user or self._password else None
            raw_connection = jaydebeapi.connect(
                self.jdbc_driver,
                jdbc_url,
                credentials,
                self.jar_file,
            )
            print("¡Conexión establecida con éxito!") # <-- DEBUG
            return raw_connection
        except Exception as exc:
            print("Error creando conexión:", exc)
            return None

    def getCursor(self):
        if self.conexion is None:
            self.conexion = self.createConnection()
        if self.conexion is None:
            return None
        return JdbcCursor(self.conexion.cursor())

    def closeConnection(self):
        try:
            if self.conexion:
                self.conexion.close()
                self.conexion = None
        except Exception as exc:
            print("Error cerrando conexión:", exc)

    def get_connection(self):
        if self.conexion is None:
            self.conexion = self.createConnection()
        return JdbcConnection(self.conexion)

    @classmethod
    def getConnection(cls):
        return cls.get_instance().get_connection()

    @staticmethod
    def close(conn):
        if conn is not None:
            conn.close()


class JdbcConnection:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return JdbcCursor(self._connection.cursor())

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        return self._connection.close()

    def __getattr__(self, name):
        return getattr(self._connection, name)
