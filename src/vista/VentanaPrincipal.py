"""
Es la ventana principal de la aplicación, que contiene un QStackedWidget con todas las pantallas.
Lo q hace es mostrar pantallas, cambiar entre ellas, guardar la sesión activa y delegar la lógica de negocio a los controladores.
"""

import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

if __package__ is None or __package__ == "":
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

from src.vista.ui.auth_window import AuthUI
from src.vista.ui.gerente_dashboard_ui import GerenteDashboardUI
from src.vista.ui.pedidos_ui import PedidosUI
from src.vista.ui.admin_dashboard_ui import AdminDashboardUI
from src.vista.ui.admin_productos_ui import AdminProductosUI
from src.vista.ui.gestion_personal_ui import GestionPersonalUI
from src.vista.ui.carta_ui import CartaUI
from src.vista.ui.cesta_ui import CestaUI
from src.vista.ui.historial_ui import HistorialUI
from src.vista.ui.fin_pedido_ui import FinPedidoUI
from src.vista.ui.confirmar_canje_ui import ConfirmarCanjeUI


class VentanaPrincipal(QMainWindow):
    """
    Vista principal de la aplicación.
    Responsabilidad:
    - Contiene el QStackedWidget con todas las pantallas.
    - Expone mostrar_widget(widget) para que cada controlador coloque su sub-vista.
    - Gestiona únicamente las pantallas sin rol único: login, panel de pedidos y
      dashboard del gerente.
    - NO construye sub-vistas de rol; eso lo hace cada Controlador.
    - NO conecta señales de sub-vistas de rol; eso lo hace cada Controlador.
    - NO contiene lógica de negocio.
    """

    def __init__(self):
        super().__init__() #hereda de QtmainWindow
        self.setWindowTitle("sushUle - Kiosco")  #texto q aparece en la barra de titulo
        self.resize(1100, 720) #tamaño inicial de la ventana
        self.setMinimumSize(900, 600) #tamaño minimo de la ventana

        #cargar el logo de la aplicación y establecerlo como icono de la ventana
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "vista", "imagenes", "logos", "sushule_logo_circulo.png",
        )
        #si el archivo existe, se establece como icono de la ventana, sino pues na
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        #SE CREA EL STACK (CONTENEDOR) DE PANTALLAS Y SE ESTABLECE COMO WIDGET CENTRAL
        self._stack = QStackedWidget() #este es el contenedor de todas las pantallas, solo una se ve cada vez
        self._stack.setStyleSheet("background-color: #147DB2;") #color de fondo del stack
        self.setCentralWidget(self._stack) #establece el stack como widget central (principal)

        #CREAR LA PANTALLA DE LOGIN Y AÑADIRLA AL STACK
        self.auth_ui = AuthUI() #crear
        self._stack.addWidget(self.auth_ui) #añadir al stack
        #ahora el stack contiene ->  [0] AuthUI


        #REFERENCIAS A CONTROLADORES
        #son None pq cuando se crea la ventana principal, los controladores aún no existen. 
        #Se inyectan después con set_controlador() 
        self._controlador = None       # ControladorPrincipal
        self._ctrl_pedidos = None      # ControladorPedidos
        self._ctrl_metricas = None     # ControladorMetricas
        self._ctrl_admin = None        # ControladorAdmin
        self._ctrl_cliente = None      # ControladorCliente

        # Estado de sesión (la vista lo guarda para devolverlo a los controladores)
        #al iniciar la aplicación no hay sesión activa, se establece cuando el usuario inicia sesión correctamente
        self._sesion_actual = None

        #REFERENCIAS A PANTALLAS TEMPORALES 
        #Sub-vistas propias de VentanaPrincipal (login, pedidos, gerente)
        """
            CUANDO HACES ir_gerente_dashboard()OCURRE ESTO: self._gerente_dashboard_widget = dashboard
            Y CUANDO HACES LOGOUT self._gerente_dashboard_widget = None
        """
        self._gerente_dashboard_widget = None
        self._pedidos_widget = None


    # ── Inyección de controladores ────────────────────────────────────────────

    #este método es llamado desde main.py para inyectar los controladores en la vista
    #en main.py se hace esto: ventana.set_controlador(controlador_principal, ctrl_admin=controlador_admin, ctrl_cliente=controlador_cliente, ctrl_pedidos=controlador_pedidos, ctrl_metricas=controlador_metricas)

    #lo que hace es guardar las referencias a los controladores y conectar las señales de login y registro a los manejadores internos de la vista
    def set_controlador(self, ctrl, ctrl_admin, ctrl_cliente, ctrl_pedidos, ctrl_metricas):
        self._controlador = ctrl
        self._ctrl_admin = ctrl_admin
        self._ctrl_cliente = ctrl_cliente
        self._ctrl_pedidos = ctrl_pedidos
        self._ctrl_metricas = ctrl_metricas

        # Inyectar fábricas de vistas — la vista conoce las vistas, el controlador no
        ctrl_admin.set_fabricas_vistas(
            fabrica_dashboard=AdminDashboardUI,
            fabrica_productos=AdminProductosUI,
            fabrica_personal=GestionPersonalUI,
        )
        ctrl_cliente.set_fabricas_vistas(
            fabrica_carta=CartaUI,
            fabrica_cesta=CestaUI,
            fabrica_historial=HistorialUI,
        )

        # Conectar señales de login y registro a manejadores internos
        #cuando el usuario hace click en login o register, se emite la señal y se llama a los métodos _handle_login y _handle_register
        self.auth_ui.login_requested.connect(self._handle_login)
        self.auth_ui.register_requested.connect(self._handle_register)

    #guarda la sesión activa en la vista, para que los controladores puedan consultarla cuando lo necesiten
    def set_sesion_actual(self, sesion):
        """Actualiza la sesión activa (llamado por ControladorPrincipal)."""
        self._sesion_actual = sesion

    #devuelve la sesión activa, para que los controladores puedan consultarla cuando lo necesiten
    def get_sesion_actual(self):
        """Devuelve la sesión activa (consultada por los controladores de rol)."""
        return self._sesion_actual


    # ── API genérica para mostrar sub-vistas ──────────────────────────────────
    def mostrar_widget(self, widget):
        """
        Añade widget al stack y lo muestra como pantalla activa.
        Cada controlador de rol llama a este método cuando quiere mostrar su sub-vista.
        """
        self._stack.addWidget(widget) #añade el widget al stack
        self._stack.setCurrentWidget(widget) #lo muestra como pantalla activa

    # ── Pantallas propias de VentanaPrincipal ─────────────────────────────────

    #son aquellas pantallas que no pertenecen a un rol específico, sino que son gestionadas por la ventana principal
    #y sus controladores asociados (login, panel de pedidos, dashboard del gerente)

    #LOGIN
    def mostrar_login(self):
        """Vuelve a la pantalla de login y limpia todos los widgets activos."""
        self._limpiar_widgets_sesion()
        self.auth_ui.clear_fields()
        self._stack.setCurrentWidget(self.auth_ui)
        self.showNormal()
        self.adjustSize()

    #DASHBOARD DEL GERENTE
    def ir_gerente_dashboard(self):
        """Construye y muestra el dashboard del gerente."""
        dashboard = GerenteDashboardUI(self._sesion_actual)
        dashboard.cerrar_sesion.connect(self.cerrar_dashboard_gerente)
        dashboard.filtro_aplicado.connect(self._recargar_dashboard_gerente)
        dashboard.rango_reseteado.connect(self._recargar_dashboard_gerente)
        dashboard.categoria_cambiada.connect(self._recargar_dashboard_gerente)
        self._gerente_dashboard_widget = dashboard
        self.mostrar_widget(dashboard)
        self._recargar_dashboard_gerente()
        self.showMaximized()

    #CERRAR SESIÓN DESDE EL DASHBOARD DEL GERENTE
    def cerrar_dashboard_gerente(self):
        if self.pedir_confirmacion("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
            self.mostrar_login()

    #PANEL DE PEDIDOS (COCINA / CAJERO) (dnd se pone si está listo, pagado...)
    def ir_panel_pedidos(self):
        """Construye y muestra el panel de pedidos (cocina / cajero)."""
        ventana_pedidos = PedidosUI() #se crea la ventana de pedidos

        #los filtros son "Todos", "Pendiente", "En preparación", "Listo para entregar", "Entregado", "Cancelado"
        filtros_disponibles = self._ctrl_pedidos.obtener_filtros_pedido_disponibles() #se obtienen los filtros disponibles desde el controlador de pedidos
        filtro_activo = self._ctrl_pedidos.obtener_filtro() #se obtiene el filtro activo desde el controlador de pedidos
        ventana_pedidos.inicializar_filtros(filtros_disponibles, filtro_activo) #se inicializan los filtros en la ventana de pedidos
        
        self._cargar_pedidos_en_vista(ventana_pedidos) #lo q hace es cargar los pedidos en la vista de pedidos, usando el filtro activo

        ventana_pedidos.cerrar_sesion.connect(self.cerrar_panel_pedidos) #lo que hace es conectar la señal de cerrar sesión de la ventana de pedidos con el método cerrar_panel_pedidos de la ventana principal

        ventana_pedidos.solicitar_ir_carta.connect(self._ctrl_cliente.ir_carta) #lo que hace es conectar la señal de solicitar ir a la carta de la ventana de pedidos con el método ir_carta del controlador de cliente

        ventana_pedidos.configurar_visibilidad_roles(self._controlador.debe_mostrar_ver_carta())#para que el botón de ver carta solo se muestre si el rol del usuario lo permite ( cajero )
        ventana_pedidos.cambio_estado_requested.connect(self._on_cambio_estado_pedido) #cuando se hace click en cambiar estado de un pedido, se llama al método _on_cambio_estado_pedido de la ventana principal

        ventana_pedidos.filtro_requested.connect(self._on_filtro_pedido) #cuando se hace click en un filtro de pedido, se llama al método _on_filtro_pedido de la ventana principal
        self._pedidos_widget = ventana_pedidos #lo que hace es guardar la referencia a la ventana de pedidos en la variable _pedidos_widget de la ventana principal
        self.mostrar_widget(ventana_pedidos) #lo que hace es mostrar la ventana de pedidos
        self.showNormal() #muestra la ventana en tamaño normal (no maximizada)
        self.adjustSize() #ajusta el tamaño de la ventana al contenido

    def cerrar_panel_pedidos(self):
        #esta función se llama cuando el usuario hace click en cerrar sesión desde el panel de pedidos, 
        #y lo que hace es preguntar al usuario si está seguro de cerrar sesión, y si lo está, 
        # llama a mostrar_login() para volver a la pantalla de login
        if self.pedir_confirmacion("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
            self.mostrar_login()

    def mostrar_fin_pedido(self, codigo, total, puntos):
        """Muestra la pantalla de confirmación de pedido completado."""
        fin = FinPedidoUI(codigo, total, puntos) #llama al constructor de FinPedidoUI para crear la pantalla de fin de pedido
        fin.volver_cesta.connect(self._ctrl_cliente.ir_cesta) #cuando se hace click en volver a la cesta, se llama al método ir_cesta del controlador de cliente
        fin.salir_login.connect(self.mostrar_login) #cuando se hace click en salir a login, se llama al método mostrar_login de la ventana principal
        self.mostrar_widget(fin) #lo que hace es mostrar la pantalla de fin de pedido

    # ── Diálogos delegados por los controladores ──────────────────────────────

    def pedir_confirmacion(self, titulo: str, mensaje: str) -> bool:
        """Muestra un diálogo de confirmación y devuelve True si el usuario acepta."""
        #esto simplememte muestra un cuadro de diálogo con un mensaje y dos botones (Sí y No), y devuelve True si el usuario hace click en Sí, o False si hace click en No
        return QMessageBox.question(
            self, titulo, mensaje,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        ) == QMessageBox.Yes
    
    def get_ctrl_cliente(self):
        #devuelve el controlador de cliente, para que otros controladores puedan acceder a él si es necesario
        return self._ctrl_cliente

    def mostrar_error(self, titulo: str, mensaje: str) -> None:
        """Muestra un diálogo de error crítico."""
        QMessageBox.critical(self, titulo, mensaje)

    def mostrar_aviso(self, titulo: str, mensaje: str) -> None:
        """Muestra un diálogo de advertencia."""
        QMessageBox.warning(self, titulo, mensaje)

    def mostrar_dialogo_canje(self, puntos: int, descuento: float) -> bool:
        """Muestra el diálogo de confirmación de canje y devuelve True si el usuario acepta."""
        dialogo = ConfirmarCanjeUI(puntos=puntos, descuento=descuento, parent=self)
        return dialogo.exec_() == ConfirmarCanjeUI.Accepted

    # ── Señales del login ─────────────────────────────────────────────────────

    def _handle_login(self, correo, contrasena):
        """
        Manejador interno de la señal login_requested de AuthUI.
        Llama al controlador para comprobar el login y manejar errores.
        """
        #si no hay un controlador conectado, muestra un error en la UI de login y retorna
        if self._controlador is None:
            self.auth_ui.show_login_error("No hay un controlador conectado.")
            return
        try: 
            #trata de comprobar el login con el controlador, que a su vez 
            #llama al modelo para verificar las credenciales en la base de datos
            sesion = self._controlador.comprobarLogin(correo, contrasena)
        except ValueError as exc:
            #si hay un error de valor (por ejemplo, campos vacíos o formato incorrecto),
            #muestra el error en la UI de login y retorna
            self.auth_ui.show_login_error(str(exc))
            return
        except RuntimeError as exc:
            #si hay un error de conexión a la base de datos, 
            #muestra un error en la UI de login y un cuadro de diálogo crítico con el mensaje del error
            self.auth_ui.show_login_error(f"Error de conexión: {exc}")
            QMessageBox.critical(self, "Error de conexión", str(exc))
            return
        except Exception as exc:
            #si hay cualquier otro error inesperado, 
            #muestra un error en la UI de login y un cuadro de diálogo crítico con el mensaje del error
            self.auth_ui.show_login_error("Error inesperado al iniciar sesión.")
            QMessageBox.critical(self, "Error inesperado", str(exc))
            return
        if not sesion:
            #si el controlador devuelve None o False, significa que las credenciales son incorrectas
            self.auth_ui.show_login_error("Usuario o contraseña incorrectos.")

    def _handle_register(self, nombre, correo, contrasena):
        """
        Manejador interno de la señal register_requested de AuthUI.
        Llama al controlador para registrar un nuevo cliente y manejar errores.
        (como handle_login, pero para registro)
        """
        #si el controlador no está conectado, muestra un error en la UI de registro y retorna
        if self._controlador is None:
            self.auth_ui.show_register_error("No hay un controlador conectado.")
            return
        try:
            #trata de registrar un nuevo cliente con el controlador, que 
            #a su vez llama al modelo para insertar el nuevo cliente en la base de datos
            sesion = self._controlador.registrar_cliente(nombre, correo, contrasena)
        except ValueError as exc:
            #si hay un error de valor (por ejemplo, campos vacíos o formato incorrecto), 
            #devuelve un error en la UI de registro y retorna
            self.auth_ui.show_register_error(str(exc))
            return
        except Exception as exc:
            #si hay cualquier otro error inesperado,
            #devuelve un error en la UI de registro y un cuadro de diálogo crítico con el mensaje del error
            self.auth_ui.show_register_error("No se pudo registrar en la base de datos.")
            QMessageBox.critical(self, "Error de registro", str(exc))
            return
        if not sesion:
            #si el controlador devuelve None o False, significa que no se pudo autenticar la nueva cuenta   
            self.auth_ui.show_register_error("No se pudo autenticar la nueva cuenta.")

    # ── Manejadores internos — pedidos ────────────────────────────────────────

    #los manejadores internos de pedidos son llamados desde la vista de pedidos (PedidosUI) cuando el usuario hace click en cambiar estado o aplicar un filtro
    #y lo que hacen es llamar al controlador de pedidos para actualizar el estado o aplicar el  filtro, y luego recargar la vista de pedidos con los datos actualizados         


    def _on_cambio_estado_pedido(self, id_num, nuevo_est):
        """
        Manejador interno de la señal cambio_estado_requested de PedidosUI.
        Llama al controlador de pedidos para actualizar el estado y recarga la vista.   
        """
        if self._ctrl_pedidos.actualizarEstado(id_num, nuevo_est):
            #si la actualización fue exitosa, recarga la vista de pedidos para reflejar el cambio
            self._cargar_pedidos_en_vista(self._pedidos_widget)
        else:
            #sino, muestra un cuadro de diálogo crítico con un mensaje de error
            QMessageBox.critical(self, "Error", "No se pudo actualizar el estado en SQL Server.")

    def _on_filtro_pedido(self, estado):
        """
        Manejador interno de la señal filtro_requested de PedidosUI.
        Llama al controlador de pedidos para establecer el filtro y recarga la vista.
        """
        self._ctrl_pedidos.establecer_filtro(estado) #establece el filtro en el controlador de pedidos
        self._cargar_pedidos_en_vista(self._pedidos_widget) #recarga la vista de pedidos para reflejar el cambio de filtro


    def _cargar_pedidos_en_vista(self, vista_pedidos):
        """
        Carga los pedidos en la vista de PedidosUI usando el filtro activo del controlador.     
        """
        if vista_pedidos is None:
            return
        pedidos = self._ctrl_pedidos.buscarPedidos() #obtiene todos los pedidos desde el controlador de pedidos
        filtro = self._ctrl_pedidos.obtener_filtro() #usa el filtro activo del controlador de pedidos (el guardado en self._ctrl_pedidos._filtro)
        plan = self._ctrl_pedidos.prepararPedidosVista(pedidos, filtro) #pasa el listado de pedidos y el filtro al controlador de pedidos para que prepare la información para la vista
        vista_pedidos.set_pedidos(plan.get("pedidos_vista", []), plan.get("mensaje", "No hay pedidos.")) #muestra los pedidos en la vista de PedidosUI, usando el plan preparado por el controlador de pedidos

    # ── Manejadores internos — gerente ────────────────────────────────────────

    #los manejadores internos de gerente son llamados desde la vista del dashboard del gerente (GerenteDashboardUI) cuando el usuario aplica un filtro, cambia la categoría o resetea el rango de fechas
    #y lo que hacen es llamar al controlador de métricas para obtener los datos actualizados

    def _recargar_dashboard_gerente(self, *args):
        """
        Manejador interno de las señales filtro_aplicado, rango_reseteado y categoria_cambiada de GerenteDashboardUI.
        Llama al controlador de métricas para obtener los datos actualizados y recarga la vista del dashboard del gerente.
        """

        #si no hay un dashboard activo o no hay un controlador de métricas conectado, retorna sin hacer nada    
        if self._gerente_dashboard_widget is None or self._ctrl_metricas is None:
            return
        vista = self._gerente_dashboard_widget #obtiene la referencia a la vista del dashboard del gerente
        fecha_inicio, fecha_fin = vista.obtener_rango_fechas() #obtiene el rango de fechas seleccionado en la vista del dashboard del gerente
        seleccion = vista.obtener_categoria_seleccionada() #obtiene la categoría seleccionada en la vista del dashboard del gerente
        order_desc = vista.obtener_orden_desc() #obtiene el orden de la gráfica (ascendente o descendente) en la vista del dashboard del gerente
        #llama al controlador de métricas para preparar el plan de datos del dashboard del gerente
        try:
            plan = self._ctrl_metricas.preparar_dashboard_gerente(
                fecha_inicio, fecha_fin, seleccion, order_desc,
            )
        #si hay un error al preparar el plan de datos, muestra un cuadro de diálogo de advertencia con el mensaje del error y retorna sin actualizar la vista
        except Exception as exc:
            QMessageBox.warning(self, "Metricas", str(exc))
            return
        #ahora actualiza la vista del dashboard del gerente con los datos obtenidos del plan
        vista.set_resumen(plan["resumen"], plan["total_empleados"])
        vista.set_empleados_texto(plan["empleados_texto"])
        vista.set_grafico(plan["grafico"]["series"], plan["grafico"]["titulo"])
        vista.inicializar_categorias(plan["categorias"]["opciones"], plan["categorias"]["seleccion"])
        vista.set_categorias_plan(plan["categorias"]["plan"])

    # ── Limpieza ──────────────────────────────────────────────────────────────

    def _limpiar_widgets_sesion(self):
        """Elimina del stack todos los widgets de sesión activa."""
        # Notificar a controladores de rol para que anulen sus referencias internas
        if self._ctrl_admin is not None:
            self._ctrl_admin.limpiar_widgets()
        if self._ctrl_cliente is not None:
            self._ctrl_cliente.limpiar_widgets()

        # Barrer el stack completo excepto auth_ui
        widgets_a_eliminar = []
        for i in range(self._stack.count()):
            w = self._stack.widget(i)
            if w is not None and w is not self.auth_ui:
                widgets_a_eliminar.append(w)
        for w in widgets_a_eliminar:
            try:
                self._stack.removeWidget(w)
            except RuntimeError:
                pass
            w.deleteLater()

        #se reinician las referencias a los widgets de sesión activa y la sesión actual
        self._gerente_dashboard_widget = None
        self._pedidos_widget = None
        self._sesion_actual = None
        #si hay un controlador principal conectado, se le notifica que la sesión actual es None (no hay sesión activa)
        if self._controlador is not None:
            self._controlador.set_sesion_actual(None)
