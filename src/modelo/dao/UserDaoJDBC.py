from src.modelo.conexion import ConexionMYSQL
from src.modelo.vo.UsuariosVo import UsuariosVo
class UserDaoJDBC(conexion):
    SQL_SELECT  = "SELECT DNO, nombre, primer_apellido, segundo_apellido, email FROM Usuarios"
    SQL_INSERT = ""
    SQL_CHECK_LOGIN = "SELECT * FROM Usuarios WHERE nombre = ? AND Contraseña ?"

    def consultarLogin(self, loginVo):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CHECK_LOGIN, (loginVo.nombre, loginVo.contrasena))
            rows = cursor.fetchone()
            
            if rows == None: 
                return None
            else: 
                dni, nombre, primer_apellido, segundo_apellido, email = rows
                usuario = UsuariosVo(dni, nombre, primer_apellido, segundo_apellido, email)

                return usuario
            
                
        except Exception as e:
            print("e")

    def select(self):
        cursor = self.getCursor()
        users = []

        try:
            cursor.execute(self.SQL_SELECT  )
            rows = cursor.fetchall()
            for row in rows:
                dni, nombre, primer_apellido, segundo_apellido, email = row
                usuario = UsuariosVo(dni, nombre, primer_apellido, segundo_apellido, email)
                users.append(usuario)
        except Exception as e:
            print(e)
