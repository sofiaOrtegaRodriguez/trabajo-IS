from src.modelo.dao.UserDaoSQLServer import UserDaoSQLServer
from src.modelo.dao.ProductoDaoSQLServer import ProductoDaoSQLServer
from src.modelo.dao.PromocionDaoSQLServer import PromocionDaoSQLServer
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

    def listarProductos(self):
        producto_dao = ProductoDaoSQLServer()
        return producto_dao.listar()

    def crearProducto(self, producto_vo):
        producto_dao = ProductoDaoSQLServer()
        return producto_dao.crear(producto_vo)

    def actualizarProducto(self, nombre_original, producto_vo):
        producto_dao = ProductoDaoSQLServer()
        return producto_dao.actualizar(nombre_original, producto_vo)

    def eliminarProducto(self, nombre_producto):
        producto_dao = ProductoDaoSQLServer()
        return producto_dao.eliminar(nombre_producto)

    def describirProductos(self):
        producto_dao = ProductoDaoSQLServer()
        return producto_dao.describir()

    def listarPromociones(self):
        promocion_dao = PromocionDaoSQLServer()
        return promocion_dao.listar()

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        promocion_dao = PromocionDaoSQLServer()
        return promocion_dao.crear(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def eliminarPromocion(self, id_promocion):
        promocion_dao = PromocionDaoSQLServer()
        return promocion_dao.eliminar(id_promocion)
