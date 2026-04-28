from PyQt5.QtWidgets import QMessageBox

from src.vista.ui.auth_window import AuthUI
from src.vista.ui.gerente_dashboard_ui import GerenteDashboardUI
from src.vista.ui.admin_dashboard_ui import AdminDashboardUI
from src.vista.ui.admin_productos_ui import AdminProductosUI
from src.vista.ui.gestion_personal_ui import GestionPersonalUI
from src.vista.ui.carta_ui import CartaUI
from src.vista.ui.cesta_ui import CestaUI
from src.vista.ui.historial_ui import HistorialUI
from src.controlador.ControladorProductos import ControladorProductos
from src.controlador.ControladorEmpleados import ControladorEmpleados
from src.modelo.ServicioCesta import ServicioCesta


class MiVentana(AuthUI):
    def __init__(self):
        super().__init__()
        self._controlador = None
        self._cliente_actual = None
        self._servicio_cesta = ServicioCesta()
        self.carta_window = None
        self.cesta_window = None
        self.historial_window = None
        self.admin_dashboard_window = None
        self.admin_productos_window = None
        self.admin_personal_window = None
        self.gerente_dashboard_window = None
        self.login_requested.connect(self.on_button_click)
        self.register_requested.connect(self.on_register_click)

    def on_button_click(self, usuario, contrasena):
        if not self._controlador:
            self.show_login_error("No hay un controlador conectado.")
            return
        try:
            sesion = self._controlador.autenticar_usuario(usuario, contrasena)
        except Exception as exc:
            self.show_login_error("No se pudo conectar con la base de datos.")
            QMessageBox.critical(self, "Error de conexion", str(exc))
            return

        if not sesion:
            self.show_login_error("Usuario o contrasena incorrectos.")
            self.show_center_popup("USUARIO O CONTRASENA INCORRECTOS")
            return

        self._route_session(sesion)

    def lanzarAvisoLogin(self):
        self.show_login_error("Usuario o contrasena incorrectos.")
        self.show_center_popup("USUARIO O CONTRASENA INCORRECTOS")

    def on_register_click(self, nombre, usuario, contrasena):
        if not self._controlador:
            self.show_register_error("No hay un controlador conectado.")
            return
        try:
            sesion = self._controlador.registrar_cliente(nombre, usuario, contrasena)
        except ValueError as exc:
            self.show_register_error(str(exc))
            return
        except Exception as exc:
            self.show_register_error("No se pudo registrar en la base de datos.")
            QMessageBox.critical(self, "Error de registro", str(exc))
            return

        if not sesion:
            self.show_register_error("No se pudo autenticar la nueva cuenta.")
            return

        self._route_session(sesion)

    def _route_session(self, sesion):
        self._cliente_actual = sesion
        if sesion.es_gerente:
            self._servicio_cesta.set_session(None)
            self._open_gerente_dashboard()
            return
        if sesion.es_administrador:
            self._servicio_cesta.set_session(None)
            self._open_admin_dashboard()
            return

        self._servicio_cesta.set_session(self._cliente_actual)
        self._open_carta()

    def _open_gerente_dashboard(self):
        self._close_client_windows()
        self._close_admin_windows()
        self._close_gerente_window()
        self.gerente_dashboard_window = GerenteDashboardUI(self._cliente_actual)
        self.gerente_dashboard_window.cerrar_sesion.connect(self._logout)
        self.gerente_dashboard_window.show()
        self.hide()

    def _open_admin_dashboard(self):
        self._close_client_windows()
        self._close_admin_windows()
        self.admin_dashboard_window = AdminDashboardUI(self._cliente_actual)
        self.admin_dashboard_window.productos_clicked.connect(self._open_admin_productos)
        self.admin_dashboard_window.personal_clicked.connect(self._open_admin_personal)
        self.admin_dashboard_window.cerrar_sesion.connect(self._logout)
        self.admin_dashboard_window.show()
        self.hide()

    def _open_admin_productos(self):
        if self.admin_dashboard_window is not None:
            self.admin_dashboard_window.hide()

        controlador_carta = ControladorProductos(self._controlador.get_modelo())
        self.admin_productos_window = AdminProductosUI(controlador=controlador_carta)
        self.admin_productos_window.volver_menu.connect(self._return_to_admin_dashboard)
        self.admin_productos_window.show()

    def _open_admin_personal(self):
        if self.admin_dashboard_window is not None:
            self.admin_dashboard_window.hide()

        controlador_empleados = ControladorEmpleados(self._controlador.get_modelo())
        self.admin_personal_window = GestionPersonalUI(controlador_empleados, self._cliente_actual)
        self.admin_personal_window.volver_menu.connect(self._return_to_admin_dashboard)
        self.admin_personal_window.cerrar_sesion.connect(self._logout)
        self.admin_personal_window.show()

    def _return_to_admin_dashboard(self):
        self._clear_admin_child_refs()
        if self.admin_dashboard_window is not None:
            self.admin_dashboard_window.show()

    def _open_carta(self):
        self._close_client_windows()
        self._close_admin_windows()
        controlador_carta = ControladorProductos(self._controlador.get_modelo())
        try:
            self.carta_window = CartaUI(
                controlador=controlador_carta,
                quantity_provider=self._servicio_cesta.cantidad_producto,
            )
        except Exception as exc:
            QMessageBox.critical(self, "Error al cargar la carta", str(exc))
            return
        self.carta_window.add_product.connect(self._add_to_cart)
        self.carta_window.remove_product.connect(self._remove_from_cart)
        self.carta_window.profile_clicked.connect(self._open_historial)
        self.carta_window.cart_clicked.connect(self._open_cesta)
        self.carta_window.show()
        self.hide()

    def _add_to_cart(self, product_id, amount):
        product = self._find_product_in_catalog(product_id)
        if product is None:
            return
        self._servicio_cesta.add_item(product, amount)
        self._refresh_carta_quantity(product_id)
        self._refresh_cesta_if_open()

    def _remove_from_cart(self, product_id):
        self._servicio_cesta.remove_item(product_id)
        self._refresh_carta_quantity(product_id)
        self._refresh_cesta_if_open()

    def _open_cesta(self):
        if self.carta_window is not None:
            self.carta_window.close()
            self.carta_window = None

        try:
            self.cesta_window = CestaUI(servicio=self._servicio_cesta)
        except Exception as exc:
            QMessageBox.critical(self, "Error al abrir la cesta", str(exc))
            return

        self.cesta_window.volver_carta.connect(self._open_carta)
        self.cesta_window.cerrar_sesion.connect(self._logout)
        self.cesta_window.show()
        self.hide()

    def _open_historial(self):
        if self.carta_window is not None:
            self.carta_window.close()
            self.carta_window = None

        try:
            pedidos = self._servicio_cesta.obtener_historial()
            self.historial_window = HistorialUI(cliente=self._cliente_actual, pedidos=pedidos)
        except Exception as exc:
            QMessageBox.critical(self, "Error al abrir el historial", str(exc))
            return

        self.historial_window.volver_menu.connect(self._open_carta)
        self.historial_window.cerrar_sesion.connect(self._logout)
        self.historial_window.show()
        self.hide()

    def _find_product_in_catalog(self, product_id):
        if self._controlador is None:
            return None

        controlador_carta = ControladorProductos(self._controlador.get_modelo())
        catalog = controlador_carta.listarProductosCarta()
        for products in catalog.values():
            for product in products:
                if product.get("id") == product_id:
                    return product
        return None

    def _refresh_cesta_if_open(self):
        if self.cesta_window is not None and hasattr(self.cesta_window, "refrescar"):
            self.cesta_window.refrescar()

    def _refresh_carta_quantity(self, product_id):
        if self.carta_window is None:
            return
        quantity = self._servicio_cesta.cantidad_producto(product_id)
        if hasattr(self.carta_window, "update_product_quantity"):
            self.carta_window.update_product_quantity(product_id, quantity)

    def _close_secondary_windows(self):
        self._close_client_windows()
        self._close_admin_windows()
        self._close_gerente_window()

    def _close_client_windows(self):
        for attr in ("carta_window", "cesta_window", "historial_window"):
            window = getattr(self, attr)
            if window is not None:
                window.close()
                setattr(self, attr, None)

    def _close_admin_children(self):
        for attr in ("admin_productos_window", "admin_personal_window"):
            window = getattr(self, attr)
            if window is not None:
                window.close()
                setattr(self, attr, None)

    def _clear_admin_child_refs(self):
        for attr in ("admin_productos_window", "admin_personal_window"):
            if getattr(self, attr) is not None:
                setattr(self, attr, None)

    def _close_admin_windows(self):
        self._close_admin_children()
        if self.admin_dashboard_window is not None:
            self.admin_dashboard_window.close()
            self.admin_dashboard_window = None

    def _close_gerente_window(self):
        if self.gerente_dashboard_window is not None:
            self.gerente_dashboard_window.close()
            self.gerente_dashboard_window = None

    def _logout(self):
        self._servicio_cesta.set_session(None)
        self._servicio_cesta.vaciar_cesta()
        self._cliente_actual = None
        self._close_secondary_windows()
        self.clear_fields()
        self.show()

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador
