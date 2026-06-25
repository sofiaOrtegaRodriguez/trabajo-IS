from src.modelo.vo.LoginVo import LoginVo


class ControladorPrincipal:
    """
    Coordina el login/registro y, tras autenticar, delega la navegación
    en el controlador de rol correspondiente. No toca widgets directamente.
    """

    def __init__(self, ref_vista, ref_modelo, ref_cesta):
        self._vista = ref_vista          # VentanaPrincipal
        self._modelo = ref_modelo        # Logica (capa de negocio)
        self._cesta = ref_cesta          # ControladorCesta
        self._sesion_actual = None

        # Controladores de rol — se inyectan desde main.py tras la construcción
        self._ctrl_admin = None
        self._ctrl_cliente = None
        self._ctrl_pedidos = None
        self._ctrl_metricas = None

    def set_controladores_rol(self, ctrl_admin, ctrl_cliente, ctrl_pedidos, ctrl_metricas):
        """Inyecta los controladores de rol una vez construidos en main.py."""
        self._ctrl_admin = ctrl_admin
        self._ctrl_pedidos = ctrl_pedidos
        self._ctrl_cliente = ctrl_cliente
        self._ctrl_metricas = ctrl_metricas

    # ── Autenticación ─────────────────────────────────────────────────────────

    def comprobarLogin(self, correo, passw):
        """
        Valida credenciales en el modelo y, si son correctas, abre la sesión.
        Devuelve el objeto sesión o None si el login falló.
        """
        resultado = self._modelo.comprobarLoginValidado(correo, passw)
        self._sesion_actual = resultado if resultado is not None else None
        if resultado is not None:
            self._abrir_sesion(resultado)
        return resultado

    def registrar_cliente(self, nombre, correo, contrasena):
        """
        Registra un nuevo cliente en el modelo y, si tiene éxito, abre su sesión.
        Devuelve el objeto sesión o None si el registro falló.
        """
        resultado = self._modelo.registrarClienteValidado(nombre, correo, contrasena)
        self._sesion_actual = resultado if resultado is not None else None
        if resultado is not None:
            self._abrir_sesion(resultado)
        return resultado

    # ── Estado de sesión ──────────────────────────────────────────────────────

    def get_sesion(self):
        """Devuelve la sesión activa o None si no hay nadie logueado."""
        return self._sesion_actual

    def set_sesion_actual(self, sesion):
        self._sesion_actual = sesion

    def debe_mostrar_ver_carta(self):
        """True si el usuario logueado es cajero (cambia el comportamiento del botón 'Ver carta')."""
        return bool(self._sesion_actual and getattr(self._sesion_actual, "es_cajero", False))

    def cerrar_sesion_desde_carta(self):
        """
        Comportamiento del botón 'Cerrar sesión' en la vista de carta:
          - Cajero → vuelve al panel de pedidos (sin confirmación).
          - Cliente → pide confirmación y vuelve al login.
        """
        if self.debe_mostrar_ver_carta():
            self._vista.ir_panel_pedidos()
        elif self._vista.pedir_confirmacion("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
            self._vista.mostrar_login()

    # ── Privados ──────────────────────────────────────────────────────────────

    def _abrir_sesion(self, sesion):
        """
        Tras autenticar, configura la sesión y navega a la pantalla inicial según el rol.

        Roles y destinos:
          VENTANA_GERENTE       → ir_gerente_dashboard()
          VENTANA_ADMINISTRADOR → ControladorAdmin.ir_dashboard()
          VENTANA_CAJERO        → ir_panel_pedidos()
          VENTANA_COCINA        → ir_panel_pedidos()  (y sin sesión en cesta)
          cualquier otro        → ControladorCliente.ir_carta()  (cliente normal)

        La cesta solo recibe sesión para cajeros y clientes; gerente, admin y cocina
        no gestionan cesta, así que se les pasa None.
        """
        self._sesion_actual = sesion
        self._vista.set_sesion_actual(sesion)

        pantalla_inicial = sesion.rol.pantalla_inicial

        # Roles sin cesta (no hacen pedidos desde su panel)
        if pantalla_inicial in ("VENTANA_GERENTE", "VENTANA_ADMINISTRADOR", "VENTANA_COCINA"):
            self._cesta.set_session(None)
        else:
            self._cesta.set_session(sesion)

        # Navegación por rol
        if pantalla_inicial == "VENTANA_GERENTE":
            self._vista.ir_gerente_dashboard()
        elif pantalla_inicial == "VENTANA_ADMINISTRADOR":
            self._ctrl_admin.ir_dashboard()
        elif pantalla_inicial in ("VENTANA_CAJERO", "VENTANA_COCINA"):
            self._vista.ir_panel_pedidos()
        else:
            self._ctrl_cliente.ir_carta()