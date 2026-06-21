"""
ControladorPrincipal
Responsabilidad:
- Coordina el inicio de sesión y el registro.
- Según el rol del usuario autenticado, delega la navegación inicial en el
  controlador de rol correspondiente.
- No manipula widgets directamente; usa métodos de VentanaPrincipal y de los
  controladores de rol.
"""

from src.modelo.vo.LoginVo import LoginVo


class ControladorPrincipal:

    def __init__(self, ref_vista, ref_modelo, ref_cesta):
        self._vista = ref_vista      # VentanaPrincipal
        self._modelo = ref_modelo    # Logica
        self._cesta = ref_cesta      # ControladorCesta
        self._sesion_actual = None

        # Controladores de rol — se inyectan desde main.py tras la construcción
        self._ctrl_admin = None
        self._ctrl_cliente = None
        self._ctrl_pedidos = None
        self._ctrl_metricas = None

    def set_controladores_rol(self, ctrl_admin, ctrl_cliente, ctrl_pedidos, ctrl_metricas):
        """Recibe los controladores de rol una vez que están construidos."""
        self._ctrl_admin = ctrl_admin
        self._ctrl_pedidos = ctrl_pedidos
        self._ctrl_cliente = ctrl_cliente
        self._ctrl_metricas = ctrl_metricas

    # ── Autenticación ─────────────────────────────────────────────────────────

    def comprobarLogin(self, correo, passw):
        resultado = self._modelo.comprobarLoginValidado(correo, passw)
        self._sesion_actual = resultado if resultado is not None else None
        if resultado is not None:
            self._abrir_sesion(resultado)
        return resultado

    def registrar_cliente(self, nombre, correo, contrasena):
        resultado = self._modelo.registrarClienteValidado(nombre, correo, contrasena)
        self._sesion_actual = resultado if resultado is not None else None
        if resultado is not None:
            self._abrir_sesion(resultado)
        return resultado

    # ── Estado de sesión ──────────────────────────────────────────────────────

    def get_sesion(self):
        return self._sesion_actual

    def set_sesion_actual(self, sesion):
        self._sesion_actual = sesion

    def debe_mostrar_ver_carta(self):
        """Devuelve True si el usuario actual es cajero."""
        return bool(self._sesion_actual and getattr(self._sesion_actual, "es_cajero", False))

    def cerrar_sesion_desde_carta(self):
        """Un cajero vuelve al panel de pedidos; un cliente vuelve al login."""
        if self.debe_mostrar_ver_carta():
            self._vista.ir_panel_pedidos()
        elif self._vista.pedir_confirmacion("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
            self._vista.mostrar_login()

    # ── Privados ──────────────────────────────────────────────────────────────

    def _abrir_sesion(self, sesion):
        self._sesion_actual = sesion
        self._vista.set_sesion_actual(sesion)

        pantalla_inicial = sesion.rol.pantalla_inicial

        if pantalla_inicial in ("VENTANA_GERENTE", "VENTANA_ADMINISTRADOR", "VENTANA_COCINA"):
            self._cesta.set_session(None)
        else:
            self._cesta.set_session(sesion)

        if pantalla_inicial == "VENTANA_GERENTE":
            self._vista.ir_gerente_dashboard()
        elif pantalla_inicial == "VENTANA_ADMINISTRADOR":
            self._ctrl_admin.ir_dashboard()
        elif pantalla_inicial in ("VENTANA_CAJERO", "VENTANA_COCINA"):
            self._vista.ir_panel_pedidos()
        else:
            self._ctrl_cliente.ir_carta()
