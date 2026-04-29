import os
import jpype
import jaydebeapi
from pathlib import Path

# 1. Ruta absoluta manual para asegurar
jar = r"C:\\trabajo-IS\\lib\\mssql-jdbc-13.4.0.jre8.jar"
driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"

try:
    print(f"Buscando archivo en: {jar}")
    if not os.path.exists(jar):
        print("ERROR: El archivo NO existe en esa ruta.")
    else:
        print("Archivo encontrado.")

    print("1. Iniciando JVM con Classpath forzado...")
    if not jpype.isJVMStarted():
        # ESTA LÍNEA ES LA CLAVE: Inicia Java con el Driver ya cargado
        jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={jar}")
    
    print("2. Registrando el Driver...")
    # Intentamos cargar la clase directamente en Java
    jpype.JClass(driver)
    print("3. ¡Driver cargado con éxito en la JVM!")

    print("4. Intentando conexión mínima...")
    # Prueba de conexión rápida
    url = "jdbc:sqlserver://127.0.0.1:1433;instanceName=SQLEXPRESS;databaseName=Sushule;encrypt=true;trustServerCertificate=true;loginTimeout=5"
    # Cambia 'app_user' y 'Admin123*' por los tuyos reales
    conn = jaydebeapi.connect(driver, url, ["app_user", "Admin123"], jar)
    print("5. ¡CONECTADO!")

except Exception as e:
    print("\n--- ERROR DETECTADO ---")
    print(e)
finally:
    if jpype.isJVMStarted():
        print("\nCerrando prueba.")