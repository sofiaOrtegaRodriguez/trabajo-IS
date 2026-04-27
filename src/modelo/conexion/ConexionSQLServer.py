import pyodbc


class ConexionSQLServer:
    _instance = None
    server = r".\SQLEXPRESS"
    database = "SushUle"
    driver = "ODBC Driver 17 for SQL Server"
    trusted_connection = "yes"
    encrypt = "no"
    trust_server_certificate = "yes"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls()

    def get_connection_string(self):
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"Trusted_Connection={self.trusted_connection};"
            f"Encrypt={self.encrypt};"
            f"TrustServerCertificate={self.trust_server_certificate};"
        )

    def get_connection(self):
        return pyodbc.connect(self.get_connection_string())

    @classmethod
    def getConnection(cls):
        return cls.get_instance().get_connection()

    @staticmethod
    def close(conn):
        if conn is not None:
            conn.close()
