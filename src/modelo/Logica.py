"""
Logica - Fachada principal de la capa de modelo.
Solo delega en servicios de negocio especializados.
"""

from src.modelo.dao.PedidoDaoJDBC import PedidoDaoJDBC
from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.logica.ServicioCesta import ServicioCesta
from src.modelo.logica.ServicioAuth import ServicioAuth
from src.modelo.logica.ServicioCarta import ServicioCarta
from src.modelo.logica.ServicioEmpleados import ServicioEmpleados
from src.modelo.logica.ServicioMetricas import ServicioMetricas
from src.modelo.logica.ServicioPedidos import ServicioPedidos
from src.modelo.logica.ServicioProductos import ServicioProductos
from src.modelo.logica.ServicioPromociones import ServicioPromociones
from src.modelo.logica.ServicioFlujoCarta import ServicioFlujoCarta



class Logica:
    def __init__(self):
        self._auth = ServicioAuth()
        self._empleados = ServicioEmpleados()
        self._productos = ServicioProductos()
        self._promociones = ServicioPromociones()
        self._pedidos = ServicioPedidos()
        self._metricas = ServicioMetricas()
        self._carta = ServicioCarta(self)
        self._flujo_carta = None

    def comprobarLogin(self, loginVo):
        return self._auth.comprobarLogin(loginVo)

    def comprobarLoginValidado(self, correo, contrasena):
        return self._auth.comprobarLoginValidado(correo, contrasena)

    def registrarCliente(self, registroVo):
        return self._auth.registrarCliente(registroVo)

    def registrarClienteValidado(self, nombre, correo, contrasena):
        return self._auth.registrarClienteValidado(nombre, correo, contrasena)

    def listarEmpleados(self):
        return self._empleados.listarEmpleados()

    def crearEmpleado(self, ssn, usuario, correo, contrasena, tipo):
        return self._empleados.crearEmpleado(ssn, usuario, correo, contrasena, tipo)

    def crearEmpleadoValidado(self, ssn, usuario, correo, contrasena, tipo):
        return self._empleados.crearEmpleadoValidado(ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        return self._empleados.actualizarEmpleado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def actualizarEmpleadoValidado(self, id_empleado, ssn, usuario, correo, contrasena, tipo):
        return self._empleados.actualizarEmpleadoValidado(id_empleado, ssn, usuario, correo, contrasena, tipo)

    def eliminarEmpleado(self, id_empleado):
        return self._empleados.eliminarEmpleado(id_empleado)

    def obtenerTiposEmpleado(self):
        return self._empleados.obtenerTiposEmpleado()

    def obtenerCategoriasAdmin(self):
        return self._empleados.obtenerCategoriasAdmin()

    def listarProductos(self):
        return self._productos.listarProductos()

    def listarProductosCarta(self):
        return self._carta.listarProductosCarta()

    def contarProductosCategoria(self, categoria):
        return self._carta.contarProductosCategoria(categoria)

    def totalPaginasCategoria(self, categoria, por_pagina=4):
        return self._carta.totalPaginasCategoria(categoria, por_pagina)

    def obtenerProductosCategoriaPaginados(self, categoria, pagina_actual, por_pagina=4):
        return self._carta.obtenerProductosCategoriaPaginados(categoria, pagina_actual, por_pagina)

    def obtenerProductosCategoriaRender(self, categoria, pagina_actual, por_pagina=4, cesta=None, image_root=None):
        return self._carta.obtenerProductosCategoriaRender(categoria, pagina_actual, por_pagina, cesta=cesta, image_root=image_root)

    def crearProducto(self, producto_vo):
        return self._productos.crearProducto(producto_vo)

    def crearProductoValidado(self, nombre, precio, ingredientes, disponible, stock, categoria):
        return self._productos.crearProductoValidado(nombre, precio, ingredientes, disponible, stock, categoria)

    def actualizarProducto(self, nombre_original, producto_vo):
        return self._productos.actualizarProducto(nombre_original, producto_vo)

    def actualizarProductoValidado(self, nombre_original, nombre, precio, ingredientes, disponible, stock, categoria):
        return self._productos.actualizarProductoValidado(nombre_original, nombre, precio, ingredientes, disponible, stock, categoria)

    def eliminarProducto(self, nombre_producto):
        return self._productos.eliminarProducto(nombre_producto)

    def describirProductos(self):
        return self._productos.describirProductos()

    def listarPromociones(self):
        return self._promociones.listarPromociones()

    def prepararPromocionesVista(self, promociones=None):
        return self._promociones.prepararPromocionesVista(promociones)

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        return self._promociones.crearPromocion(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def crearPromocionValidada(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        return self._promociones.crearPromocionValidada(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def eliminarPromocion(self, id_promocion):
        return self._promociones.eliminarPromocion(id_promocion)

    def crearPedido(self, sesion, items, total):
        return self._pedidos.crearPedido(sesion, items, total)

    def listarPedidos(self, sesion):
        return self._pedidos.listarPedidos(sesion)

    def listarTodosPedidos(self):
        return self._pedidos.listarTodosPedidos()

    def filtrarPedidosPorEstado(self, pedidos, estado="TODOS"):
        return self._pedidos.filtrarPedidosPorEstado(pedidos, estado)

    def prepararPedidosVista(self, pedidos, estado="TODOS"):
        return self._pedidos.prepararPedidosVista(pedidos, estado)

    def establecerFiltroPedidos(self, estado="TODOS"):
        return str(estado).strip().upper() or "TODOS"

    def obtenerFiltroPedidos(self):
        return "TODOS"

    def prepararPedidosVistaActual(self, pedidos=None):
        if pedidos is None:
            pedidos = self.listarTodosPedidos()
        return self.prepararPedidosVista(pedidos, self.obtenerFiltroPedidos())

    def obtenerEstadosPedidoPermitidos(self):
        return self._pedidos.obtenerEstadosPedidoPermitidos()

    def obtenerFiltrosPedidoDisponibles(self):
        return self._pedidos.obtenerFiltrosPedidoDisponibles()

    def actualizarEstadoPedido(self, pedido):
        return self._pedidos.actualizarEstadoPedido(pedido)

    def sumarPuntosCliente(self, id_cliente, puntos):
        
        return UserDaoJDBC().actualizarPuntos(id_cliente, puntos)

    def obtenerMetricasGerente(self, fecha_inicio=None, fecha_fin=None):
        return self._metricas.obtenerMetricasGerente(fecha_inicio, fecha_fin)

    def prepararDashboardGerenteVista(self, fecha_inicio=None, fecha_fin=None, seleccion_categoria="Todas las categorias", order_desc=True):
        return self._metricas.prepararDashboardGerenteVista(fecha_inicio, fecha_fin, seleccion_categoria, order_desc)

    def prepararCategoriasMetricas(self, categorias, seleccion="Todas las categorias", order_desc=True):
        return self._metricas.prepararCategoriasMetricas(categorias, seleccion, order_desc)

    def crear_servicio_cesta(self):
        return ServicioCesta(PedidoDaoJDBC(), UserDaoJDBC())

    def crear_servicio_flujo_carta(self, cesta):
        self._flujo_carta = ServicioFlujoCarta(self, cesta)
        return self._flujo_carta
