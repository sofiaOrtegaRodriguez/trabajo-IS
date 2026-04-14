import pyodbc


class ConexionSQLServer:
    server = r".\SQLEXPRESS"
    database = "SushUle"
    driver = "ODBC Driver 17 for SQL Server"
    trusted_connection = "yes"
    encrypt = "no"
    trust_server_certificate = "yes"

    @classmethod
    def get_connection_string(cls):
        return (
            f"DRIVER={{{cls.driver}}};"
            f"SERVER={cls.server};"
            f"DATABASE={cls.database};"
            f"Trusted_Connection={cls.trusted_connection};"
            f"Encrypt={cls.encrypt};"
            f"TrustServerCertificate={cls.trust_server_certificate};"
        )

    @classmethod
    def getConnection(cls):
        return pyodbc.connect(cls.get_connection_string())

    @staticmethod
    def close(conn):
        if conn is not None:
            conn.close()
