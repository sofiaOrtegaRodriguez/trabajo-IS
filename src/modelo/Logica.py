from src.modelo.dao.UserDaoSQLServer import UserDaoSQLServer
class Logica():
    def ejemploSelect(self):
        userDAO = UserDaoSQLServer()
        usuarios = userDAO.select()
        for user in usuarios:
            print(user)
            print(user.nombre)

    def comprobarLogin(self, loginVo):
        login_dao = UserDaoSQLServer()
        return login_dao.consultarLogin(loginVo)

    def registrarCliente(self, nombre, correo, contrasena):
        login_dao = UserDaoSQLServer()
        return login_dao.registrarCliente(nombre, correo, contrasena)
