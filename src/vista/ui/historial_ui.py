"""
Vista del Historial de Pedidos - PyQt5.

Este archivo contiene dos clases:
  - PedidoCard: widget que representa visualmente un pedido individual
  - HistorialUI: pantalla completa del historial de pedidos del cliente

Patrón MVC: pura VISTA. No contiene lógica de negocio.
Los datos llegan ya preparados desde el controlador en el constructor.
Esta vista NO usa señales para pedir datos: los recibe al instanciarse.
"""

import os

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QVBoxLayout

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES DE COLOR locales (no se importan de auth_common porque esta
# pantalla tiene su propia paleta azul/naranja/rojo para pedidos cancelados)
# ─────────────────────────────────────────────────────────────────────────────
C_BG = "#147DB2"      # azul fondo general
C_CARD = "#5CA9D0"    # azul claro para cards de pedidos completados
C_ORANGE = "#FC814A"  # naranja para acentos de pedidos completados
C_WHITE = "#FFFFFF"
C_MUTED = "#B6D5E2"   # azul pálido para texto secundario / mensaje de vacío
C_RED_BG = "#4A2020"  # fondo oscuro rojizo para pedidos cancelados
C_RED_ACC = "#C06060" # acento rojo para detalles de pedidos cancelados


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENTE AUXILIAR: tarjeta de un pedido individual
# ─────────────────────────────────────────────────────────────────────────────

class PedidoCard(QFrame):
    """
    Widget que representa visualmente un pedido individual en el historial.

    Carga su estructura desde PedidoCardUI.ui y la rellena con los datos
    del VO de pedido recibido. Cambia de paleta de colores según el estado:
      - Completado: fondo azul claro, acento naranja
      - Cancelado:  fondo rojo oscuro, acento rojo claro

    Estructura visual (definida en PedidoCardUI.ui):
      ┌────────────────────────────────────────┐
      │ ▌ barEstado   Pedido #XXXX  [Estado]   │
      │              Fecha     Hora            │
      │              · Producto x2   X.XX €   │
      │              · Producto x1   X.XX €   │
      │                             Total €   │
      └────────────────────────────────────────┘
    """

    def __init__(self, pedido, parent=None):
        super().__init__(parent)
        # Carga el .ui sobre self: todos los widgets quedan como atributos de self
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", "PedidoCardUI.ui")
        uic.loadUi(ui_path, self)
        # Rellena la card con los datos del pedido inmediatamente
        self._render(pedido)

    def _render(self, pedido):
        """
        Rellena todos los elementos visuales de la card con los datos del pedido.

        Decide la paleta de colores según el estado del pedido:
          - Si estado == "cancelado" → paleta roja
          - Cualquier otro estado    → paleta azul/naranja (completado)
        """
        cancelado = pedido.estado == "cancelado"

        # Selección de colores según el estado
        bg = C_RED_BG if cancelado else C_CARD          # color de fondo de la card
        accent = C_RED_ACC if cancelado else C_ORANGE   # color de la barra lateral y detalles
        estado_bg = C_RED_ACC if cancelado else C_BG    # color de fondo del badge de estado
        estado_txt = "X  Cancelado" if cancelado else "✓  Completado"

        # Estilo del frame principal: fondo y bordes redondeados
        # El selector QFrame#PedidoCardUI apunta por nombre de objeto (objectName del .ui)
        self.setStyleSheet(f"QFrame#PedidoCardUI{{background:{bg};border-radius:18px;}}QLabel{{background:transparent;}}")

        # Barra lateral de color (indicador visual del estado)
        bar_estado = self.findChild(QFrame, "barEstado")
        if bar_estado is not None:
            bar_estado.setStyleSheet(f"background:{accent};border-radius:3px;")

        # Rellena los labels con los datos del pedido
        self.lblId.setText(f"Pedido #{pedido.id:04d}")  # :04d → número con 4 dígitos (ej. #0007)

        # Badge de estado con fondo de color
        self.lblBadgeEstado.setText(estado_txt)
        self.lblBadgeEstado.setStyleSheet(
            f"background:{estado_bg};color:{C_WHITE};font-size:11px;font-weight:700;border-radius:10px;padding:4px 12px;"
        )

        self.lblHora.setText(f"{pedido.fecha}     {pedido.hora}")
        self.lblTotal.setText(f"{pedido.total:.2f} €")

        # Construye el texto de detalle de productos: una línea por producto
        detalle = []
        for prod in pedido.productos:
            detalle.append(f"· {prod.nombre_producto} x{prod.cantidad}   {prod.subtotal:.2f} €")
        # Si no hay productos (caso raro), muestra un mensaje en lugar de una lista vacía
        self.lblProductos.setText("\n".join(detalle) if detalle else "Sin productos registrados.")


# ─────────────────────────────────────────────────────────────────────────────
# VISTA PRINCIPAL: pantalla de historial de pedidos
# ─────────────────────────────────────────────────────────────────────────────

class HistorialUI(QWidget):
    """
    Pantalla de historial de pedidos del cliente.

    Recibe los datos ya preparados en el constructor (cliente y pedidos),
    por lo que NO necesita señales para pedir datos al controlador.
    Solo emite señales para navegación (volver al menú, cerrar sesión).

    Estructura visual (definida en HistorialUI.ui):
      ┌──────────────────────────────────────────┐
      │ [Volver]  lblBienvenida  [puntos] [Logout]│  ← header
      ├──────────────────────────────────────────┤
      │ lblNumPedidos                             │
      │  ┌─────────────────────────────────────┐ │
      │  │ PedidoCard #1                       │ │
      │  ├─────────────────────────────────────┤ │
      │  │ PedidoCard #2                       │ │  ← itemsLayout (scroll)
      │  └─────────────────────────────────────┘ │
      └──────────────────────────────────────────┘

    SEÑALES (vista → controlador):
    """

    # Se emite cuando el usuario pulsa "Volver al menú"
    volver_menu = pyqtSignal()

    # Se emite cuando el usuario pulsa "Cerrar sesión"
    cerrar_sesion = pyqtSignal()

    def __init__(self, cliente, pedidos, parent=None):
        super().__init__(parent)
        self._cliente = cliente   # VO del cliente (para mostrar nombre y puntos)
        self._pedidos = pedidos   # lista de VOs de pedido ya preparados por el controlador

        # Carga el .ui sobre self
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", "HistorialUI.ui")
        uic.loadUi(ui_path, self)

        # itemsLayout es el QVBoxLayout donde se añaden las PedidoCard dinámicamente
        self.itemsLayout = self.findChild(QVBoxLayout, "itemsLayout")

        self._connect_signals()  # conecta botones a sus emisores de señal
        self._render()           # rellena el header y genera las cards

    # ─────────────────────────────────────────────────────────────
    # CONEXIÓN DE SEÑALES
    # ─────────────────────────────────────────────────────────────

    def _connect_signals(self):
        """
        Conecta los botones del .ui a los métodos internos de la vista.
        btnBack y btnLogout son atributos inyectados por uic.loadUi.
        """
        self.btnBack.clicked.connect(self.volver_menu)          # emite directamente la señal
        self.btnLogout.clicked.connect(self._confirmar_cierre)  # pasa por un método intermedio

    # ─────────────────────────────────────────────────────────────
    # RENDERIZADO
    # ─────────────────────────────────────────────────────────────

    def _render(self):
        """Punto de entrada del renderizado: llama al header y a los items."""
        self._render_header()
        self._render_items()

    def _render_header(self):
        """
        Rellena los labels del header con los datos del cliente:
          - puntos del cliente
          - nombre de bienvenida
          - número de pedidos registrados (con pluralización correcta)
        """
        self.lblPuntos.setText(str(self._cliente.puntos))
        self.lblBienvenida.setText(f"Bienvenid@, {self._cliente.nombre}")

        n = len(self._pedidos)
        # Pluralización: "1 pedido registrado" vs "3 pedidos registrados"
        self.lblNumPedidos.setText(f"{n} pedido{'s' if n != 1 else ''} registrado{'s' if n != 1 else ''}")

    def _render_items(self):
        """
        Genera y añade una PedidoCard por cada pedido en itemsLayout.

        Primero limpia el layout (por si se llamara a _render más de una vez).
        Si no hay pedidos, muestra un label de "sin pedidos" en su lugar.
        """
        self._clear_layout(self.itemsLayout)

        if not self._pedidos:
            # Caso sin pedidos: muestra mensaje centrado en color atenuado
            lbl_empty = QLabel("Aún no tienes pedidos registrados.")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet(f"color:{C_MUTED};font-size:15px;font-weight:600;")
            self.itemsLayout.addWidget(lbl_empty)
            return

        # Crea una PedidoCard por cada pedido y la añade al layout
        for pedido in self._pedidos:
            self.itemsLayout.addWidget(PedidoCard(pedido))

    def _clear_layout(self, layout):
        """
        Elimina todos los widgets del layout dado, liberando su memoria.

        Usa takeAt(0) en bucle en lugar de iterar directamente para evitar
        problemas con el índice al modificar el layout mientras se recorre.
        deleteLater() programa la destrucción del widget de forma segura
        (Qt la ejecuta en el siguiente ciclo del event loop).
        """
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)   # extrae y elimina el primer item del layout
            widget = item.widget()
            if widget:
                widget.deleteLater()  # libera la memoria del widget de forma segura

    # ─────────────────────────────────────────────────────────────
    # EMISIÓN DE SEÑALES
    # ─────────────────────────────────────────────────────────────

    def _confirmar_cierre(self):
        """
        Emite cerrar_sesion cuando el usuario pulsa "Cerrar sesión".
        El método intermedio existe por si en el examen piden añadir
        un QMessageBox de confirmación antes de cerrar: este sería el lugar.
        """
        self.cerrar_sesion.emit()