from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.dao.EmpleadoDaoJDBC import EmpleadoDaoJDBC
from src.modelo.dao.ProductoDaoJDBC import ProductoDaoJDBC
from src.modelo.dao.PromocionDaoJDBC import PromocionDaoJDBC
from src.modelo.dao.PedidoDaoJDBC import PedidoDaoJDBC
from src.modelo.dao.MetricasDaoJDBC import MetricasDaoJDBC
class Logica():
    def ejemploSelect(self):
        userDAO = UserDaoJDBC()
        usuarios = userDAO.select()
        for user in usuarios:
            print(user)
            print(user.nombre)

    def comprobarLogin(self, loginVo):
        login_dao = UserDaoJDBC()
        sesion = login_dao.consultarLogin(loginVo)
        if sesion is not None:
            return sesion
        empleado_dao = EmpleadoDaoJDBC()
        return empleado_dao.consultarLogin(loginVo)

    def registrarCliente(self, nombre, correo, contrasena):
        login_dao = UserDaoJDBC()
        return login_dao.registrarCliente(nombre, correo, contrasena)

    def listarEmpleados(self):
        empleado_dao = EmpleadoDaoJDBC()
        return empleado_dao.listar()

    def crearEmpleado(self, ssn, usuario, correo, contrasena, tipo):
        empleado_dao = EmpleadoDaoJDBC()
        return empleado_dao.crear(ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        empleado_dao = EmpleadoDaoJDBC()
        return empleado_dao.actualizar(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def eliminarEmpleado(self, id_empleado):
        empleado_dao = EmpleadoDaoJDBC()
        return empleado_dao.eliminar(id_empleado)

    def listarProductos(self):
        producto_dao = ProductoDaoJDBC()
        return producto_dao.listar()

    def crearProducto(self, producto_vo):
        producto_dao = ProductoDaoJDBC()
        return producto_dao.crear(producto_vo)

    def actualizarProducto(self, nombre_original, producto_vo):
        producto_dao = ProductoDaoJDBC()
        return producto_dao.actualizar(nombre_original, producto_vo)

    def eliminarProducto(self, nombre_producto):
        producto_dao = ProductoDaoJDBC()
        return producto_dao.eliminar(nombre_producto)

    def describirProductos(self):
        producto_dao = ProductoDaoJDBC()
        return producto_dao.describir()

    def listarPromociones(self):
        promocion_dao = PromocionDaoJDBC()
        return promocion_dao.listar()

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        promocion_dao = PromocionDaoJDBC()
        return promocion_dao.crear(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def eliminarPromocion(self, id_promocion):
        promocion_dao = PromocionDaoJDBC()
        return promocion_dao.eliminar(id_promocion)

    def crearPedido(self, sesion, items, total):
        pedido_dao = PedidoDaoJDBC()
        return pedido_dao.crear(sesion, items, total)

    def listarPedidos(self, sesion):
        pedido_dao = PedidoDaoJDBC()
        return pedido_dao.listar(sesion)
    
    def listarTodosPedidos(self):
        pedido_dao = PedidoDaoJDBC()
        return pedido_dao.listarTiempoReal()
    
    def actualizarEstadoPedido(self, pedido):
        pedido_dao = PedidoDaoJDBC()
        return pedido_dao.modificarEstado(pedido)

    def sumarPuntosCliente(self, id_cliente, puntos):
        user_dao = UserDaoJDBC()
        return user_dao.actualizarPuntos(id_cliente, puntos)

    def obtenerMetricasGerente(self, fecha_inicio=None, fecha_fin=None):
        metrica_dao = MetricasDaoJDBC()
        return metrica_dao.obtener_metricas(fecha_inicio, fecha_fin)
