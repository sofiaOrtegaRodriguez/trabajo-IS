from src.modelo.dao.UserDaoSQLServer import UserDaoSQLServer
from src.modelo.dao.EmpleadoDaoSQLServer import EmpleadoDaoSQLServer
from src.modelo.dao.ProductoDaoSQLServer import ProductoDaoSQLServer
from src.modelo.dao.PromocionDaoSQLServer import PromocionDaoSQLServer
from src.modelo.dao.PedidoDaoSQLServer import PedidoDaoSQLServer
from src.modelo.dao.MetricasDaoSQLServer import MetricasDaoSQLServer
class Logica():
    def ejemploSelect(self):
        userDAO = UserDaoSQLServer()
        usuarios = userDAO.select()
        for user in usuarios:
            print(user)
            print(user.nombre)

    def comprobarLogin(self, loginVo):
        login_dao = UserDaoSQLServer()
        sesion = login_dao.consultarLogin(loginVo)
        if sesion is not None:
            return sesion
        empleado_dao = EmpleadoDaoSQLServer()
        return empleado_dao.consultarLogin(loginVo)

    def registrarCliente(self, nombre, correo, contrasena):
        login_dao = UserDaoSQLServer()
        return login_dao.registrarCliente(nombre, correo, contrasena)

    def listarEmpleados(self):
        empleado_dao = EmpleadoDaoSQLServer()
        return empleado_dao.listar()

    def crearEmpleado(self, ssn, usuario, correo, contrasena, tipo):
        empleado_dao = EmpleadoDaoSQLServer()
        return empleado_dao.crear(ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        empleado_dao = EmpleadoDaoSQLServer()
        return empleado_dao.actualizar(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def eliminarEmpleado(self, id_empleado):
        empleado_dao = EmpleadoDaoSQLServer()
        return empleado_dao.eliminar(id_empleado)

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

    def crearPedido(self, sesion, items, total):
        pedido_dao = PedidoDaoSQLServer()
        return pedido_dao.crear(sesion, items, total)

    def listarPedidos(self, sesion):
        pedido_dao = PedidoDaoSQLServer()
        return pedido_dao.listar(sesion)
    
    def listarTodosPedidos(self):
        pedido_dao = PedidoDaoSQLServer()
        return pedido_dao.listarTiempoReal()
    
    def actualizarEstadoPedido(self, pedido):
        pedido_dao = PedidoDaoSQLServer()
        return pedido_dao.modificarEstado(pedido)

    def sumarPuntosCliente(self, id_cliente, puntos):
        user_dao = UserDaoSQLServer()
        return user_dao.actualizarPuntos(id_cliente, puntos)

    def obtenerMetricasGerente(self, fecha_inicio=None, fecha_fin=None):
        metrica_dao = MetricasDaoSQLServer()
        return metrica_dao.obtener_metricas(fecha_inicio, fecha_fin)
