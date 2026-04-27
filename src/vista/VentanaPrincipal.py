import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

if __package__ is None or __package__ == "":
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

from src.controlador.ControladorProductos import ControladorProductos
from src.controlador.ControladorEmpleados import ControladorEmpleados
from src.controlador.ControladorMetricas import ControladorMetricas
from src.modelo.ServicioCesta import ServicioCesta
from src.vista.ui.gerente_dashboard_ui import GerenteDashboardUI
from src.vista.ui.admin_dashboard_ui import AdminDashboardUI
from src.vista.ui.admin_productos_ui import AdminProductosUI
from src.vista.ui.auth_window import AuthUI
from src.vista.ui.carta_ui import CartaUI
from src.vista.ui.cesta_ui import CestaUI
from src.vista.ui.gestion_personal_ui import GestionPersonalUI
from src.vista.ui.historial_ui import HistorialUI


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("sushUle - Kiosco")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "vista",
            "imagenes",
            "logos",
            "sushule_logo_circulo.png",
        )
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background-color: #147DB2;")
        self.setCentralWidget(self._stack)

        self.auth_ui = AuthUI()
        self._stack.addWidget(self.auth_ui)

        self._controlador = None
        self._controlador_productos = None
        self._servicio_cesta = ServicioCesta()
        self._cliente_actual = None
        self._catalogo_por_id = {}

        self._carta_widget = None
        self._cesta_widget = None
        self._historial_widget = None
        self._admin_dashboard_widget = None
        self._admin_productos_widget = None
        self._admin_personal_widget = None
        self._gerente_dashboard_widget = None

    def set_controlador(self, ctrl):
        self._controlador = ctrl
        self.auth_ui.login_requested.connect(self._handle_login)
        self.auth_ui.register_requested.connect(self._handle_register)

    def _handle_login(self, nombre, contrasena):
        if self._controlador is None:
            self.auth_ui.show_login_error("No hay un controlador conectado.")
            return

        try:
            sesion = self._controlador.comprobarLogin(nombre, contrasena)
        except Exception as exc:
            self.auth_ui.show_login_error("No se pudo conectar con la base de datos.")
            QMessageBox.critical(self, "Error de conexion", str(exc))
            return

        if not sesion:
            self.auth_ui.show_login_error("Usuario o contrasena incorrectos.")
            return

        self._cliente_actual = sesion
        if sesion.es_gerente:
            self._servicio_cesta.set_session(None)
            self.mostrar_gerente_dashboard()
            return
        if sesion.es_administrador:
            self._servicio_cesta.set_session(None)
            self.mostrar_admin_dashboard()
            return
        self._servicio_cesta.set_session(self._cliente_actual)
        self.mostrar_carta()

    def _handle_register(self, nombre, correo, contrasena):
        if self._controlador is None:
            self.auth_ui.show_register_error("No hay un controlador conectado.")
            return

        try:
            self._controlador.registrarCliente(nombre, correo, contrasena)
        except ValueError as exc:
            self.auth_ui.show_register_error(str(exc))
            return
        except Exception as exc:
            self.auth_ui.show_register_error("No se pudo registrar en la base de datos.")
            QMessageBox.critical(self, "Error de registro", str(exc))
            return

        try:
            sesion = self._controlador.comprobarLogin(correo, contrasena)
        except Exception as exc:
            self.auth_ui.show_register_error("No se pudo autenticar la nueva cuenta.")
            QMessageBox.critical(self, "Error de autenticacion", str(exc))
            return
        self._cliente_actual = sesion
        if sesion.es_gerente:
            self._servicio_cesta.set_session(None)
            self.mostrar_gerente_dashboard()
            return
        if sesion.es_administrador:
            self._servicio_cesta.set_session(None)
            self.mostrar_admin_dashboard()
            return
        self._servicio_cesta.set_session(self._cliente_actual)
        self.mostrar_carta()

    def _replace_widget(self, old, new):
        if old is not None:
            self._stack.removeWidget(old)
            old.deleteLater()
        self._stack.addWidget(new)
        self._stack.setCurrentWidget(new)

    def mostrar_login(self):
        self._close_admin_children()
        for attr in ("_carta_widget", "_cesta_widget", "_historial_widget"):
            widget = getattr(self, attr)
            if widget is not None:
                self._stack.removeWidget(widget)
                widget.deleteLater()
                setattr(self, attr, None)

        for attr in ("_admin_dashboard_widget", "_admin_productos_widget", "_admin_personal_widget"):
            widget = getattr(self, attr)
            if widget is not None:
                try:
                    self._stack.removeWidget(widget)
                except Exception:
                    pass
                widget.deleteLater()
                setattr(self, attr, None)
        if self._gerente_dashboard_widget is not None:
            try:
                self._stack.removeWidget(self._gerente_dashboard_widget)
            except Exception:
                pass
            self._gerente_dashboard_widget.deleteLater()
            self._gerente_dashboard_widget = None

        self._catalogo_por_id = {}
        self._cliente_actual = None
        self._servicio_cesta.set_session(None)
        self._servicio_cesta.vaciar_cesta()
        self.auth_ui.clear_fields()
        self._stack.setCurrentWidget(self.auth_ui)

    def mostrar_admin_dashboard(self):
        if self._controlador is None:
            return

        self._close_gerente_dashboard()
        self._close_admin_children()
        dashboard = AdminDashboardUI(self._cliente_actual)
        dashboard.productos_clicked.connect(self.mostrar_admin_productos)
        dashboard.personal_clicked.connect(self.mostrar_admin_personal)
        dashboard.cerrar_sesion.connect(self.mostrar_login)

        self._replace_widget(self._admin_dashboard_widget, dashboard)
        self._admin_dashboard_widget = dashboard

    def mostrar_gerente_dashboard(self):
        if self._controlador is None:
            return

        self._close_admin_windows()
        self._close_admin_children()

        dashboard = GerenteDashboardUI(self._cliente_actual, ControladorMetricas(self._controlador.get_modelo()))
        dashboard.cerrar_sesion.connect(self.mostrar_login)
        self._replace_widget(self._gerente_dashboard_widget, dashboard)
        self._gerente_dashboard_widget = dashboard

    def mostrar_admin_productos(self):
        self._close_admin_children()
        if self._admin_dashboard_widget is not None:
            self._admin_dashboard_widget.hide()

        controlador_productos = ControladorProductos(self._controlador.get_modelo())
        ventana = AdminProductosUI(controlador=controlador_productos)
        ventana.volver_menu.connect(self._volver_admin_dashboard)
        ventana.show()
        self._admin_productos_widget = ventana

    def mostrar_admin_personal(self):
        self._close_admin_children()
        if self._admin_dashboard_widget is not None:
            self._admin_dashboard_widget.hide()

        controlador_empleados = ControladorEmpleados(self._controlador.get_modelo())
        ventana = GestionPersonalUI(controlador_empleados, self._cliente_actual)
        ventana.volver_menu.connect(self._volver_admin_dashboard)
        ventana.cerrar_sesion.connect(self.mostrar_login)
        ventana.show()
        self._admin_personal_widget = ventana

    def _volver_admin_dashboard(self):
        self._clear_admin_child_refs()
        if self._admin_dashboard_widget is not None:
            self._admin_dashboard_widget.show()
            self._stack.setCurrentWidget(self._admin_dashboard_widget)

    def mostrar_carta(self):
        if self._controlador is None:
            return

        controlador_productos = ControladorProductos(self._controlador.get_modelo())
        self._controlador_productos = controlador_productos

        try:
            nueva_carta = CartaUI(
                controlador=controlador_productos,
                quantity_provider=self._servicio_cesta.cantidad_producto,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error al cargar la carta",
                str(exc),
            )
            self.mostrar_login()
            return

        nueva_carta.add_product.connect(self._add_to_cart)
        nueva_carta.remove_product.connect(self._remove_from_cart)
        nueva_carta.cart_clicked.connect(self.mostrar_cesta)
        nueva_carta.profile_clicked.connect(self.mostrar_historial)
        nueva_carta.cerrar_sesion.connect(self.mostrar_login)

        self._catalogo_por_id = self._build_catalog_index(controlador_productos)

        self._replace_widget(self._carta_widget, nueva_carta)
        self._carta_widget = nueva_carta

    def _close_admin_children(self):
        for attr in ("_admin_productos_widget", "_admin_personal_widget"):
            widget = getattr(self, attr)
            if widget is not None:
                widget.close()
                setattr(self, attr, None)

    def _close_gerente_dashboard(self):
        if self._gerente_dashboard_widget is not None:
            self._gerente_dashboard_widget.close()
            self._gerente_dashboard_widget = None

    def _clear_admin_child_refs(self):
        for attr in ("_admin_productos_widget", "_admin_personal_widget"):
            if getattr(self, attr) is not None:
                setattr(self, attr, None)

    def mostrar_cesta(self):
        nueva_cesta = CestaUI(servicio=self._servicio_cesta, cliente=self._cliente_actual)
        nueva_cesta.volver_carta.connect(self.mostrar_carta)
        nueva_cesta.cerrar_sesion.connect(self.mostrar_login)

        self._replace_widget(self._cesta_widget, nueva_cesta)
        self._cesta_widget = nueva_cesta

    def mostrar_historial(self):
        pedidos = self._servicio_cesta.obtener_historial()
        nuevo_historial = HistorialUI(cliente=self._cliente_actual, pedidos=pedidos)
        nuevo_historial.volver_menu.connect(self.mostrar_carta)
        nuevo_historial.cerrar_sesion.connect(self.mostrar_login)

        self._replace_widget(self._historial_widget, nuevo_historial)
        self._historial_widget = nuevo_historial

    def _build_catalog_index(self, controlador_productos):
        catalogo = {}
        for products in controlador_productos.listarProductosCarta().values():
            for product in products:
                catalogo[product["id"]] = product
        return catalogo

    def _add_to_cart(self, product_id, amount):
        product = self._catalogo_por_id.get(product_id)
        if product is None:
            return
        self._servicio_cesta.add_item(product, amount)
        self._refresh_carta_quantity(product_id)
        if self._cesta_widget is not None:
            self._cesta_widget.refresh()

    def _remove_from_cart(self, product_id):
        self._servicio_cesta.remove_item(product_id)
        self._refresh_carta_quantity(product_id)
        if self._cesta_widget is not None:
            self._cesta_widget.refresh()

    def _refresh_carta_quantity(self, product_id):
        if self._carta_widget is None:
            return
        quantity = self._servicio_cesta.cantidad_producto(product_id)
        if hasattr(self._carta_widget, "update_product_quantity"):
            self._carta_widget.update_product_quantity(product_id, quantity)
