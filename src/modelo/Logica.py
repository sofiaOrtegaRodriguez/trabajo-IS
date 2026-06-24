"""
Logica - Fachada principal de la capa de modelo.
Solo delega en servicios de negocio especializados.

Esta clase implementa el patrón FACHADA (Facade):
  - Es el único punto de entrada que los controladores usan para acceder
    a toda la lógica de negocio y los datos.
  - No contiene lógica propia: cada método delega inmediatamente en el
    servicio especializado correspondiente.
  - Los controladores nunca instancian ni conocen los servicios directamente;
    solo conocen a Logica.
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

    # ─────────────────────────────────────────────────────────────
    # CONSTRUCTOR: instancia todos los servicios
    # ─────────────────────────────────────────────────────────────

    def __init__(self):
        # Cada servicio se instancia una sola vez y se reutiliza durante toda la sesión
        self._auth = ServicioAuth()
        self._empleados = ServicioEmpleados()
        self._productos = ServicioProductos()
        self._promociones = ServicioPromociones()
        self._pedidos = ServicioPedidos()
        self._metricas = ServicioMetricas()
        # ServicioCarta recibe self (la propia Logica) porque necesita llamar
        # a otros métodos de Logica para obtener productos y promociones
        self._carta = ServicioCarta(self)
        # ServicioFlujoCarta se crea bajo demanda en crear_servicio_flujo_carta(),
        # porque necesita una cesta ya construida como parámetro
        self._flujo_carta = None

    # ─────────────────────────────────────────────────────────────
    # AUTH: login y registro
    # ─────────────────────────────────────────────────────────────

    def comprobarLogin(self, loginVo):
        """Comprueba las credenciales sin validar. Delega en ServicioAuth."""
        return self._auth.comprobarLogin(loginVo)

    def comprobarLoginValidado(self, correo, contrasena):
        """Valida formato y comprueba credenciales. Delega en ServicioAuth."""
        return self._auth.comprobarLoginValidado(correo, contrasena)

    def registrarCliente(self, registroVo):
        """Registra un cliente sin validar. Delega en ServicioAuth."""
        return self._auth.registrarCliente(registroVo)

    def registrarClienteValidado(self, nombre, correo, contrasena):
        """Valida datos y registra un cliente. Delega en ServicioAuth."""
        return self._auth.registrarClienteValidado(nombre, correo, contrasena)

    # ─────────────────────────────────────────────────────────────
    # EMPLEADOS: CRUD y valores fijos
    # ─────────────────────────────────────────────────────────────

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
        """Devuelve la lista fija de tipos de empleado válidos: ["CAJERO", "COCINA"]."""
        return self._empleados.obtenerTiposEmpleado()

    def obtenerCategoriasAdmin(self):
        """Devuelve la lista fija de categorías de producto: ["Sushi", "Fritos", "Postres", "Bebidas"]."""
        return self._empleados.obtenerCategoriasAdmin()

    # ─────────────────────────────────────────────────────────────
    # PRODUCTOS: CRUD, carta y esquema de BD
    # ─────────────────────────────────────────────────────────────

    def listarProductos(self):
        """Devuelve todos los productos del DAO (sin paginación ni filtros)."""
        return self._productos.listarProductos()

    def listarProductosCarta(self):
        """Devuelve los productos disponibles para mostrar en la carta del cliente."""
        return self._carta.listarProductosCarta()

    def contarProductosCategoria(self, categoria):
        """Cuenta cuántos productos hay en una categoría (para paginación)."""
        return self._carta.contarProductosCategoria(categoria)

    def totalPaginasCategoria(self, categoria, por_pagina=4):
        """Calcula el número total de páginas de una categoría dado un tamaño de página."""
        return self._carta.totalPaginasCategoria(categoria, por_pagina)

    def obtenerProductosCategoriaPaginados(self, categoria, pagina_actual, por_pagina=4):
        """Devuelve los productos de una categoría para una página concreta."""
        return self._carta.obtenerProductosCategoriaPaginados(categoria, pagina_actual, por_pagina)

    def obtenerProductosCategoriaRender(self, categoria, pagina_actual, por_pagina=4, cesta=None, image_root=None):
        """Devuelve los productos de una categoría preparados para renderizar en la vista."""
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
        """Devuelve el esquema de la tabla PRODUCTOS (columnas, tipos).
        Usado para detectar si la BD tiene columna de categoría."""
        return self._productos.describirProductos()

    # ─────────────────────────────────────────────────────────────
    # PROMOCIONES: CRUD y preparación para la vista
    # ─────────────────────────────────────────────────────────────

    def listarPromociones(self):
        return self._promociones.listarPromociones()

    def prepararPromocionesVista(self, promociones=None):
        """Transforma los VOs de promoción en dicts listos para la tabla de la vista."""
        return self._promociones.prepararPromocionesVista(promociones)

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        return self._promociones.crearPromocion(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def crearPromocionValidada(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        return self._promociones.crearPromocionValidada(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def eliminarPromocion(self, id_promocion):
        return self._promociones.eliminarPromocion(id_promocion)

    # ─────────────────────────────────────────────────────────────
    # PEDIDOS: creación, listado, filtrado y estados
    # ─────────────────────────────────────────────────────────────

    def crearPedido(self, sesion, items, total):
        return self._pedidos.crearPedido(sesion, items, total)

    def listarPedidos(self, sesion):
        """Devuelve los pedidos del cliente de la sesión actual."""
        return self._pedidos.listarPedidos(sesion)

    def listarTodosPedidos(self):
        """Devuelve todos los pedidos (para roles con acceso completo: cajero, cocina, gerente)."""
        return self._pedidos.listarTodosPedidos()

    def filtrarPedidosPorEstado(self, pedidos, estado="TODOS"):
        return self._pedidos.filtrarPedidosPorEstado(pedidos, estado)

    def prepararPedidosVista(self, pedidos, estado="TODOS"):
        """Transforma los VOs de pedido en dicts listos para la vista, con el filtro aplicado."""
        return self._pedidos.prepararPedidosVista(pedidos, estado)

    def establecerFiltroPedidos(self, estado="TODOS"):
        """Normaliza el valor del filtro de estado (mayúsculas, sin espacios)."""
        return str(estado).strip().upper() or "TODOS"

    def obtenerFiltroPedidos(self):
        """Devuelve el filtro activo actual. Por defecto siempre es "TODOS"."""
        return "TODOS"

    def prepararPedidosVistaActual(self, pedidos=None):
        """
        Prepara la vista de pedidos con el filtro activo.
        Si no se pasan pedidos, los obtiene todos de la BD.
        Combina listarTodosPedidos + prepararPedidosVista en un único paso.
        """
        if pedidos is None:
            pedidos = self.listarTodosPedidos()
        return self.prepararPedidosVista(pedidos, self.obtenerFiltroPedidos())

    def obtenerEstadosPedidoPermitidos(self):
        """Devuelve los estados válidos por los que puede pasar un pedido."""
        return self._pedidos.obtenerEstadosPedidoPermitidos()

    def obtenerFiltrosPedidoDisponibles(self):
        """Devuelve los filtros de estado disponibles en la vista de pedidos."""
        return self._pedidos.obtenerFiltrosPedidoDisponibles()

    def actualizarEstadoPedido(self, pedido):
        """Avanza el estado de un pedido al siguiente permitido."""
        return self._pedidos.actualizarEstadoPedido(pedido)

    # ─────────────────────────────────────────────────────────────
    # PUNTOS DE CLIENTE
    # ─────────────────────────────────────────────────────────────

    def sumarPuntosCliente(self, id_cliente, puntos):
        """
        Suma puntos al cliente indicado.
        NOTA: es el único método de Logica que llama directamente a un DAO
        (UserDaoJDBC) sin pasar por un servicio. Podría refactorizarse
        moviéndolo a ServicioAuth o a un ServicioClientes futuro.
        """
        return UserDaoJDBC().actualizarPuntos(id_cliente, puntos)

    # ─────────────────────────────────────────────────────────────
    # MÉTRICAS: dashboard del gerente
    # ─────────────────────────────────────────────────────────────

    def obtenerMetricasGerente(self, fecha_inicio=None, fecha_fin=None):
        """Devuelve los datos crudos del DAO de métricas para el rango indicado."""
        return self._metricas.obtenerMetricasGerente(fecha_inicio, fecha_fin)

    def prepararDashboardGerenteVista(self, fecha_inicio=None, fecha_fin=None, seleccion_categoria="Todas las categorias", order_desc=True):
        """Transforma todos los datos de métricas en la estructura lista para la vista del dashboard."""
        return self._metricas.prepararDashboardGerenteVista(fecha_inicio, fecha_fin, seleccion_categoria, order_desc)

    def prepararCategoriasMetricas(self, categorias, seleccion="Todas las categorias", order_desc=True):
        """Genera el plan de bloques del ranking de categorías para la vista."""
        return self._metricas.prepararCategoriasMetricas(categorias, seleccion, order_desc)

    # ─────────────────────────────────────────────────────────────
    # FACTORIES: creación de servicios con estado propio
    # ─────────────────────────────────────────────────────────────

    def crear_servicio_cesta(self):
        """
        Crea y devuelve una nueva instancia de ServicioCesta.
        ServicioCesta tiene estado propio (los items añadidos por el cliente),
        por eso se crea bajo demanda y no en el constructor.
        Recibe los DAOs que necesita como dependencias inyectadas.
        """
        return ServicioCesta(PedidoDaoJDBC(), UserDaoJDBC())

    def crear_servicio_flujo_carta(self, cesta):
        """
        Crea y devuelve una nueva instancia de ServicioFlujoCarta.
        Necesita la cesta ya construida como parámetro porque gestiona
        el flujo de navegación entre pantallas de la carta junto con el estado de la cesta.
        Guarda la referencia en self._flujo_carta para que pueda consultarse después.
        """
        self._flujo_carta = ServicioFlujoCarta(self, cesta)
        return self._flujo_carta