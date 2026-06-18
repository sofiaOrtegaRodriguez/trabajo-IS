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
        super().__init__()
        self.setWindowTitle("sushUle - Kiosco")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "vista", "imagenes", "logos", "sushule_logo_circulo.png",
        )
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background-color: #147DB2;")
        self.setCentralWidget(self._stack)

        self.auth_ui = AuthUI()
        self._stack.addWidget(self.auth_ui)

        # Referencias a controladores — se inyectan desde main.py
        self._controlador = None       # ControladorPrincipal
        self._ctrl_pedidos = None      # ControladorPedidos
        self._ctrl_metricas = None     # ControladorMetricas
        self._ctrl_admin = None        # ControladorAdmin
        self._ctrl_cliente = None      # ControladorCliente

        # Estado de sesión (la vista lo guarda para devolverlo a los controladores)
        self._sesion_actual = None

        # Sub-vistas propias de VentanaPrincipal (login, pedidos, gerente)
        self._gerente_dashboard_widget = None
        self._pedidos_widget = None


    # ── Inyección de controladores ────────────────────────────────────────────

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

        self.auth_ui.login_requested.connect(self._handle_login)
        self.auth_ui.register_requested.connect(self._handle_register)

    def set_sesion_actual(self, sesion):
        """Actualiza la sesión activa (llamado por ControladorPrincipal)."""
        self._sesion_actual = sesion

    def get_sesion_actual(self):
        """Devuelve la sesión activa (consultada por los controladores de rol)."""
        return self._sesion_actual

    # ── API genérica para mostrar sub-vistas ──────────────────────────────────

    def mostrar_widget(self, widget):
        """
        Añade widget al stack y lo muestra como pantalla activa.
        Cada controlador de rol llama a este método cuando quiere mostrar su sub-vista.
        """
        self._stack.addWidget(widget)
        self._stack.setCurrentWidget(widget)

    # ── Pantallas propias de VentanaPrincipal ─────────────────────────────────

    def mostrar_login(self):
        """Vuelve a la pantalla de login y limpia todos los widgets activos."""
        self._limpiar_widgets_sesion()
        self.auth_ui.clear_fields()
        self._stack.setCurrentWidget(self.auth_ui)
        self.showNormal()
        self.adjustSize()

    def ir_gerente_dashboard(self):
        """Construye y muestra el dashboard del gerente."""
        dashboard = GerenteDashboardUI(self._sesion_actual)
        dashboard.cerrar_sesion.connect(self.mostrar_login)
        dashboard.filtro_aplicado.connect(self._recargar_dashboard_gerente)
        dashboard.rango_reseteado.connect(self._recargar_dashboard_gerente)
        dashboard.categoria_cambiada.connect(self._recargar_dashboard_gerente)
        self._gerente_dashboard_widget = dashboard
        self.mostrar_widget(dashboard)
        self._recargar_dashboard_gerente()
        self.showMaximized()

    def ir_panel_pedidos(self):
        """Construye y muestra el panel de pedidos (cocina / cajero)."""
        ventana_pedidos = PedidosUI()
        filtros_disponibles = self._ctrl_pedidos.obtener_filtros_pedido_disponibles()
        filtro_activo = self._ctrl_pedidos.obtener_filtro()
        ventana_pedidos.inicializar_filtros(filtros_disponibles, filtro_activo)
        self._cargar_pedidos_en_vista(ventana_pedidos)
        ventana_pedidos.cerrar_sesion.connect(self.mostrar_login)
        ventana_pedidos.solicitar_ir_carta.connect(self._ctrl_cliente.ir_carta)
        ventana_pedidos.configurar_visibilidad_roles(self._controlador.debe_mostrar_ver_carta())
        ventana_pedidos.cambio_estado_requested.connect(self._on_cambio_estado_pedido)
        ventana_pedidos.filtro_requested.connect(self._on_filtro_pedido)
        self._pedidos_widget = ventana_pedidos
        self.mostrar_widget(ventana_pedidos)
        self.showNormal()
        self.adjustSize()

    def mostrar_fin_pedido(self, codigo, total, puntos):
        """Muestra la pantalla de confirmación de pedido completado."""
        from src.vista.ui.fin_pedido_ui import FinPedidoUI
        fin = FinPedidoUI(codigo, total, puntos)
        fin.volver_cesta.connect(self._ctrl_cliente.ir_cesta)
        fin.salir_login.connect(self.mostrar_login)
        self.mostrar_widget(fin)

    # ── Diálogos delegados por los controladores ──────────────────────────────

    def pedir_confirmacion(self, titulo: str, mensaje: str) -> bool:
        """Muestra un diálogo de confirmación y devuelve True si el usuario acepta."""
        return QMessageBox.question(
            self, titulo, mensaje,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        ) == QMessageBox.Yes
    
    def get_ctrl_cliente(self):
        return self._ctrl_cliente

    def mostrar_error(self, titulo: str, mensaje: str) -> None:
        """Muestra un diálogo de error crítico."""
        QMessageBox.critical(self, titulo, mensaje)

    def mostrar_aviso(self, titulo: str, mensaje: str) -> None:
        """Muestra un diálogo de advertencia."""
        QMessageBox.warning(self, titulo, mensaje)

    def mostrar_dialogo_canje(self, puntos: int, descuento: float) -> bool:
        """Muestra el diálogo de confirmación de canje y devuelve True si el usuario acepta."""
        from src.vista.ui.confirmar_canje_ui import ConfirmarCanjeUI
        dialogo = ConfirmarCanjeUI(puntos=puntos, descuento=descuento, parent=self)
        return dialogo.exec_() == ConfirmarCanjeUI.Accepted

    # ── Señales del login ─────────────────────────────────────────────────────

    def _handle_login(self, correo, contrasena):
        if self._controlador is None:
            self.auth_ui.show_login_error("No hay un controlador conectado.")
            return
        try:
            sesion = self._controlador.comprobarLogin(correo, contrasena)
        except ValueError as exc:
            self.auth_ui.show_login_error(str(exc))
            return
        except RuntimeError as exc:
            self.auth_ui.show_login_error(f"Error de conexión: {exc}")
            QMessageBox.critical(self, "Error de conexión", str(exc))
            return
        except Exception as exc:
            self.auth_ui.show_login_error("Error inesperado al iniciar sesión.")
            QMessageBox.critical(self, "Error inesperado", str(exc))
            return
        if not sesion:
            self.auth_ui.show_login_error("Usuario o contraseña incorrectos.")

    def _handle_register(self, nombre, correo, contrasena):
        if self._controlador is None:
            self.auth_ui.show_register_error("No hay un controlador conectado.")
            return
        try:
            sesion = self._controlador.registrar_cliente(nombre, correo, contrasena)
        except ValueError as exc:
            self.auth_ui.show_register_error(str(exc))
            return
        except Exception as exc:
            self.auth_ui.show_register_error("No se pudo registrar en la base de datos.")
            QMessageBox.critical(self, "Error de registro", str(exc))
            return
        if not sesion:
            self.auth_ui.show_register_error("No se pudo autenticar la nueva cuenta.")

    # ── Manejadores internos — pedidos ────────────────────────────────────────

    def _on_cambio_estado_pedido(self, id_num, nuevo_est):
        if self._ctrl_pedidos.actualizarEstado(id_num, nuevo_est):
            self._cargar_pedidos_en_vista(self._pedidos_widget)
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar el estado en SQL Server.")

    def _on_filtro_pedido(self, estado):
        self._ctrl_pedidos.establecer_filtro(estado)
        self._cargar_pedidos_en_vista(self._pedidos_widget)

    def _cargar_pedidos_en_vista(self, vista_pedidos):
        if vista_pedidos is None:
            return
        pedidos = self._ctrl_pedidos.buscarPedidos()
        filtro = self._ctrl_pedidos.obtener_filtro()          # ← usa el filtro guardado
        plan = self._ctrl_pedidos.prepararPedidosVista(pedidos, filtro)   # ← pásalo aquí
        vista_pedidos.set_pedidos(plan.get("pedidos_vista", []), plan.get("mensaje", "No hay pedidos."))

    # ── Manejadores internos — gerente ────────────────────────────────────────

    def _recargar_dashboard_gerente(self, *args):
        if self._gerente_dashboard_widget is None or self._ctrl_metricas is None:
            return
        vista = self._gerente_dashboard_widget
        fecha_inicio, fecha_fin = vista.obtener_rango_fechas()
        seleccion = vista.obtener_categoria_seleccionada()
        order_desc = vista.obtener_orden_desc()
        try:
            plan = self._ctrl_metricas.preparar_dashboard_gerente(
                fecha_inicio, fecha_fin, seleccion, order_desc,
            )
        except Exception as exc:
            QMessageBox.warning(self, "Metricas", str(exc))
            return
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

        self._gerente_dashboard_widget = None
        self._pedidos_widget = None
        self._sesion_actual = None
        if self._controlador is not None:
            self._controlador.set_sesion_actual(None)
