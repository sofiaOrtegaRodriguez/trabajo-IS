
import os

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

#primero se intenta importar los colores desde auth_common.py, 
#si falla, se definen valores por defecto
try:
    from src.vista.ui.auth_common import (
        C_BACKGROUND,
        C_CARD,
        C_CREAM,
        C_ORANGE,
        C_ORANGE_DARK,
        C_TEXT_MUTED,
    )
except ImportError:
    C_BACKGROUND, C_CARD, C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_MUTED = (
        "#147DB2",
        "#072D44",
        "#FEF5ED",
        "#FC814A",
        "#E66E3A",
        "#B6D5E2",
    )



"""
    Esta clase representa la interfaz de usuario para la gestión de pedidos en la aplicación.
    Hereda de QWidget y utiliza un archivo .ui (del Designer de Qt) para definir su diseño.
    Proporciona señales para indicar cuando se solicita cerrar sesión, cambiar el estado de un pedido   
    o navegar a la carta de productos. Además, incluye métodos para inicializar filtros de estado, establecer la lista de pedidos 
    y renderizar (construir o actualizar lo que el usuario ve en pantalla a partir de unos datos)las tarjetas de pedido en la interfaz.


"""

"""
    En este archivo hay dos clases principales: PedidoAdminCard y PedidosUI.

    PedidoAdminCard representa una tarjeta individual de pedido, mostrando información como el ID del pedido,   
    el cliente, la hora, los productos y el estado del pedido. También permite cambiar el estado del pedido mediante un selector (QComboBox).

    PedidosUI representa la interfaz completa de gestión de pedidos, incluyendo un contenedor para las
    tarjetas de pedido y botones para cerrar sesión o navegar a la carta de productos.

"""
class PedidoAdminCard(QFrame):

    """Tarjeta individual de pedido en la interfaz de administración de pedidos."""
    #señal que se emite cuando se solicita un cambio de estado para un pedido específico.
    cambio_estado_requested = pyqtSignal(int, str)

    def __init__(self, pedido, parent=None):
        super().__init__(parent) #hereda del constructor de QFrame y establece el widget padre si se proporciona

        #carga el archivo .ui que define el diseño de la tarjeta de pedido
        ui_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ui_pyqt",
            "PedidoAdminCardUI.ui"
        )
        uic.loadUi(ui_path, self) #carga el diseño del archivo .ui en la instancia actual de PedidoAdminCard

        #renderiza la tarjeta de pedido con la información proporcionada en el diccionario 'pedido'
        self._render(pedido)


    #función que renderiza la tarjeta de pedido con la información proporcionada en el diccionario 'pedido'
    def _render(self, pedido):
        #se obtienen los estilos de la tarjeta de pedido desde el diccionario 'pedido',
        style = pedido.get("estilo", {})
        #se definen los colores de acento, fondo y texto a partir de los estilos obtenidos,
        accent = style.get("accent", C_ORANGE)
        #se definen los colores de fondo y texto a partir de los estilos obtenidos, con valores por defecto si no se encuentran en el diccionario
        bg = style.get("bg", C_CARD)
        #se define el color de texto a partir de los estilos obtenidos, con un valor por defecto si no se encuentra en el diccionario
        text_color = style.get("text", C_CREAM)

        #se establece la hoja de estilo (CSS) para la tarjeta de pedido, incluyendo el color de fondo, borde y radio de borde, así como el estilo del QLabel
        self.setStyleSheet(
            f"QFrame#PedidoAdminCardUI {{ background-color: {C_CARD}; border: 1px solid rgba(252,129,74,0.2);"
            f" border-left: 6px solid {accent}; border-radius: 12px; }} QLabel {{ background: transparent; }}"
        )

        #aqui se define un efecto de sombra para la tarjeta de pedido, con un radio de desenfoque, color y desplazamiento específicos
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        #aquo se establecen los textos de los QLabel en la tarjeta de pedido utilizando la información proporcionada en el diccionario 'pedido'
        self.lblId.setText(f"Pedido #{pedido.get('id')}")
        self.lblCliente.setText(f"Cliente: {pedido.get('cliente', 'Anonimo')} • {pedido.get('origen', 'Kiosco')}")
        self.lblHora.setText(f"Hora: {pedido.get('hora_texto', '--:--:--')}")
        self.lblProductos.setText(pedido.get("texto_productos", "Sin productos registrados."))
        self.lblTotal.setText(f"{float(pedido.get('total', 0)):.2f} €")

        #aqui se establece el estado del pedido en la tarjeta, incluyendo el texto y los estilos de color de fondo y texto
        estado_display = pedido.get("estado_display", "")
        self.lblBadgeEstado.setText(estado_display.upper())
        self.lblBadgeEstado.setStyleSheet(
            f"background-color: {bg}; color: {text_color}; border: 1px solid {accent};"
            " border-radius: 6px; font-size: 11px; font-weight: 800; padding: 4px 12px; letter-spacing: 0.5px;"
        )

        #aqui se obtiene la lista de estados permitidos para el pedido y se agregan al selector de estado (QComboBox)
        estados_permitidos = list(pedido.get("estados_permitidos", []) or [])
        self.selectorEstado.addItems(estados_permitidos)
        self.selectorEstado.setCurrentText(estado_display)

        #aqui se conecta la señal currentTextChanged del selector de estado a una función lambda que emite la señal cambio_estado_requested con el ID del pedido y el nuevo estado seleccionado
        pedido_id = int(pedido.get("id"))
        self.selectorEstado.currentTextChanged.connect(
            lambda nuevo_estado, pid=pedido_id: self.cambio_estado_requested.emit(pid, nuevo_estado.upper())
        )


class PedidosUI(QWidget):
    """Interfaz de usuario para la gestión de pedidos en la aplicación."""

    #señales que se emiten cuando el usuario interactúa con la interfaz de pedidos
    cerrar_sesion = pyqtSignal() #cerrar sesión
    cambio_estado_requested = pyqtSignal(int, str)  #cambio de estado de un pedido, emite el ID del pedido y el nuevo estado
    solicitar_ir_carta = pyqtSignal() #navegar a la carta de productos
    filtro_requested = pyqtSignal(str) #cambio de filtro de estado, emite el estado seleccionado para filtrar los pedidos

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pedidos = [] #se hace una lista vacía para almacenar los pedidos que se mostrarán en la interfaz
        self.botones_filtro = {} #diccionario para almacenar los botones de filtro de estado, donde la clave es el estado y el valor es el botón correspondiente
        self._filtro_activo = "TODOS" #variable para almacenar el estado de filtro actualmente activo, inicializado como "TODOS"
        self._mensaje_vacio = "No hay pedidos para mostrar." #mensaje que se mostrará cuando no haya pedidos para mostrar en la interfaz

        #aqui se carga el archivo .ui que define el diseño de la interfaz de pedidos, buscando primero "pedidosUI.ui" y luego "PedidosUI.ui" si el primero no existe
        ui_dir = os.path.join(os.path.dirname(__file__), "..", "ui_pyqt")
        ui_path = os.path.join(ui_dir, "pedidosUI.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(ui_dir, "PedidosUI.ui")
        uic.loadUi(ui_path, self)

        #aqui se obtienen los layouts de los contenedores de filtros y tarjetas de pedido para poder manipularlos posteriormente
        self.filtrosLayout = self.filtrosContenedor.layout()
        self.cardsLayout = self.contenidoScroll.layout()

        #aqui se conectan las señales de los botones y campos de entrada a los métodos correspondientes
        self._connect_signals()

    #función que conecta las señales de los botones y campos de entrada a los métodos correspondientes
    def _connect_signals(self):
        self.btnCerrarSesion.clicked.connect(lambda: self.cerrar_sesion.emit())
        self.btnIrCarta.clicked.connect(lambda: self.solicitar_ir_carta.emit())

    #función que inicializa los filtros de estado en la interfaz de pedidos, creando botones para cada estado y conectando sus señales a la señal filtro_requested
    def inicializar_filtros(self, estados, filtro_activo="TODOS"):
        self._clear_layout(self.filtrosLayout)
        self.botones_filtro.clear()
        self._filtro_activo = str(filtro_activo).strip().upper() or "TODOS"

        """
        Para cada estado en la lista de estados proporcionada, se crea un botón con el texto del estado, se configura su apariencia y comportamiento, y se agrega al layout de filtros.
        Además, se conecta la señal toggled del botón a una función que actualiza los estilos   
        de los botones de filtro y la señal clicked del botón a una función que emite la señal filtro_requested con el estado correspondiente.
        """
        for estado in list(estados or []):
            estado_texto = str(estado).strip().upper()
            if not estado_texto:
                continue
            boton = QPushButton(estado_texto)
            boton.setCursor(Qt.PointingHandCursor)
            boton.setCheckable(True)
            boton.setAutoExclusive(True)
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            boton.toggled.connect(lambda checked: self._actualizar_estilos_filtros())
            boton.clicked.connect(lambda checked, est=estado_texto: self.filtro_requested.emit(est))
            boton.setChecked(estado_texto == self._filtro_activo)
            self.filtrosLayout.addWidget(boton)
            self.botones_filtro[estado_texto] = boton

        #aqui se actualizan los estilos de los botones de filtro para reflejar el estado activo y los estados inactivos
        self._actualizar_estilos_filtros()

    #función que establece la lista de pedidos en la interfaz de pedidos, actualizando la lista interna y renderizando las tarjetas de pedido correspondientes
    def set_pedidos(self, lista_pedidos, mensaje_vacio="No hay pedidos para mostrar."):
        self.pedidos = list(lista_pedidos or [])
        self._mensaje_vacio = mensaje_vacio
        self._render_pedidos()

    #función que configura la visibilidad del botón para ir a la carta de productos, mostrando u ocultando el botón según el valor de mostrar_carta
    def configurar_visibilidad_roles(self, mostrar_carta=False):
        self.btnIrCarta.setVisible(bool(mostrar_carta))

    #función que limpia un layout dado, eliminando todos los widgets hijos y liberando la memoria asociada
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    #función que actualiza los estilos de los botones de filtro para reflejar el estado activo y los estados inactivos
    def _actualizar_estilos_filtros(self):
        if not self.botones_filtro:
            return
        for estado, boton in self.botones_filtro.items():
            if boton.isChecked():
                boton.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {C_ORANGE}; border: none; border-radius: 15px;
                        color: {C_CARD}; font-weight: 800; padding: 8px 0px; font-size: 12px;
                        text-align: center;
                    }}
                """)
            else:
                boton.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {C_CARD}; border: 1px solid rgba(254, 245, 237, 0.2);
                        border-radius: 15px; color: {C_TEXT_MUTED}; font-weight: 600;
                        padding: 8px 0px; font-size: 12px; text-align: center;
                    }}
                    QPushButton:hover {{ background-color: #0B3E5C; color: {C_CREAM}; }}
                """)

    #función que limpia las tarjetas de pedido del layout de tarjetas, eliminando todos los widgets hijos y liberando la memoria asociada
    def _clear_cards(self):
        while self.cardsLayout.count():
            item = self.cardsLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    #función que renderiza (construye o actualiza lo que el usuario ve en pantalla a partir de unos datos) las tarjetas de pedido en la interfaz, mostrando un mensaje si no hay pedidos para mostrar
    def _render_pedidos(self):
        self._clear_cards()

        if not self.pedidos:
            vacio = QLabel(self._mensaje_vacio)
            vacio.setAlignment(Qt.AlignCenter)
            vacio.setStyleSheet(
                f"font-size: 16px; color: {C_TEXT_MUTED}; font-style: italic;"
                " padding: 40px; background: transparent;"
            )
            self.cardsLayout.addWidget(vacio)
            self.cardsLayout.addStretch()
            return

        for pedido in self.pedidos:
            card = PedidoAdminCard(pedido)
            card.cambio_estado_requested.connect(self.cambio_estado_requested)
            self.cardsLayout.addWidget(card)

        self.cardsLayout.addStretch()
