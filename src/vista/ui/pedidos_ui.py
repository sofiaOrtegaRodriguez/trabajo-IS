"""
Vista del Panel de Pedidos en Tiempo Real — PyQt5.
"""

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


class PedidoAdminCard(QFrame):
    cambio_estado_requested = pyqtSignal(int, str)

    def __init__(self, pedido, parent=None):
        super().__init__(parent)

        ui_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ui_pyqt",
            "PedidoAdminCardUI.ui"
        )
        uic.loadUi(ui_path, self)

        self._render(pedido)

    def _render(self, pedido):
        style = pedido.get("estilo", {})
        accent = style.get("accent", C_ORANGE)
        bg = style.get("bg", C_CARD)
        text_color = style.get("text", C_CREAM)

        self.setStyleSheet(
            f"QFrame#PedidoAdminCardUI {{ background-color: {C_CARD}; border: 1px solid rgba(252,129,74,0.2);"
            f" border-left: 6px solid {accent}; border-radius: 12px; }} QLabel {{ background: transparent; }}"
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.lblId.setText(f"Pedido #{pedido.get('id')}")
        self.lblCliente.setText(f"Cliente: {pedido.get('cliente', 'Anonimo')} • {pedido.get('origen', 'Kiosco')}")
        self.lblHora.setText(f"Hora: {pedido.get('hora_texto', '--:--:--')}")
        self.lblProductos.setText(pedido.get("texto_productos", "Sin productos registrados."))
        self.lblTotal.setText(f"{float(pedido.get('total', 0)):.2f} €")

        estado_display = pedido.get("estado_display", "")
        self.lblBadgeEstado.setText(estado_display.upper())
        self.lblBadgeEstado.setStyleSheet(
            f"background-color: {bg}; color: {text_color}; border: 1px solid {accent};"
            " border-radius: 6px; font-size: 11px; font-weight: 800; padding: 4px 12px; letter-spacing: 0.5px;"
        )

        estados_permitidos = list(pedido.get("estados_permitidos", []) or [])
        self.selectorEstado.addItems(estados_permitidos)
        self.selectorEstado.setCurrentText(estado_display)

        pedido_id = int(pedido.get("id"))
        self.selectorEstado.currentTextChanged.connect(
            lambda nuevo_estado, pid=pedido_id: self.cambio_estado_requested.emit(pid, nuevo_estado.upper())
        )


class PedidosUI(QWidget):
    cerrar_sesion = pyqtSignal()
    cambio_estado_requested = pyqtSignal(int, str)
    solicitar_ir_carta = pyqtSignal()
    filtro_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pedidos = []
        self.botones_filtro = {}
        self._filtro_activo = "TODOS"
        self._mensaje_vacio = "No hay pedidos para mostrar."

        ui_dir = os.path.join(os.path.dirname(__file__), "..", "ui_pyqt")
        ui_path = os.path.join(ui_dir, "pedidosUI.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(ui_dir, "PedidosUI.ui")
        uic.loadUi(ui_path, self)

        self.filtrosLayout = self.filtrosContenedor.layout()
        self.cardsLayout = self.contenidoScroll.layout()

        self._connect_signals()

    def _connect_signals(self):
        self.btnCerrarSesion.clicked.connect(lambda: self.cerrar_sesion.emit())
        self.btnIrCarta.clicked.connect(lambda: self.solicitar_ir_carta.emit())

    def inicializar_filtros(self, estados, filtro_activo="TODOS"):
        self._clear_layout(self.filtrosLayout)
        self.botones_filtro.clear()
        self._filtro_activo = str(filtro_activo).strip().upper() or "TODOS"

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

        self._actualizar_estilos_filtros()

    def set_pedidos(self, lista_pedidos, mensaje_vacio="No hay pedidos para mostrar."):
        self.pedidos = list(lista_pedidos or [])
        self._mensaje_vacio = mensaje_vacio
        self._render_pedidos()

    def configurar_visibilidad_roles(self, mostrar_carta=False):
        self.btnIrCarta.setVisible(bool(mostrar_carta))

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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

    def _clear_cards(self):
        while self.cardsLayout.count():
            item = self.cardsLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
