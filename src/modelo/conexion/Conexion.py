import jaydebeapi

class Conexion:
    def __init__(self, host='AMELIA\\SQLEXPRESS', database='Sushule', user='', password=''):
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self.conexion = self.createConnection()

    def createConnection(self):
        try:
            jdbc_driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
            jar_file = "lib/mssql-jdbc-12.6.1.jre11.jar"
            self.conexion = jaydebeapi.connect(
                jdbc_driver,
                f"jdbc:sqlserver://{self._host};databaseName={self._database};integratedSecurity=true;encrypt=true;trustServerCertificate=true",
                None,
                jar_file
            )
            return self.conexion
        except Exception as e:
            print("Error creando conexión:", e)
            return None

    """Un cursor es una estructura de control que permite recorrer los resultados de una 
    consulta SQL y manipular fila por fila los datos recuperados desde una base de datos."""
    def getCursor(self):
        if self.conexion is None:
            self.createConnection()
        return self.conexion.cursor()

    def closeConnection(self):
        try:
            if self.conexion:
                self.conexion.close()
                self.conexion = None
        except Exception as e:
            print("Error cerrando conexión:", e)

