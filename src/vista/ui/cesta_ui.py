import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal


class CestaUI(QWidget):
    volver_carta = pyqtSignal()
    cerrar_sesion = pyqtSignal()

    eliminar_requested = pyqtSignal(str)

    canjear_requested = pyqtSignal()
    finalizar_requested = pyqtSignal()
    abandonar_requested = pyqtSignal()

    def __init__(self, items=None, resumen=None, cliente=None):
        super().__init__()

        self._items = items or []
        self._resumen = resumen or {}
        self._cliente = cliente

        ui_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ui_pyqt",
            "CestaUI.ui"
        )

        uic.loadUi(ui_path, self)

        # Layout REAL donde se pintan items (esto es clave)
        self.itemsLayout = self.findChild(QVBoxLayout, "itemsLayout")

        self._connect_signals()
        self._render()

    # -------------------------
    # CONEXIONES
    # -------------------------
    def _connect_signals(self):
        self.btnBack.clicked.connect(self.volver_carta)
        self.btnCanjear.clicked.connect(self.canjear_requested)
        self.btnFinalizar.clicked.connect(self.finalizar_requested)
        self.btnAbandonar.clicked.connect(self.abandonar_requested)

    # -------------------------
    # API externa (tu VentanaPrincipal)
    # -------------------------
    def set_estado(self, items, resumen, cliente=None):
        self._items = items
        self._resumen = resumen or {}
        self._cliente = cliente
        self._render()

    def mostrar_mensaje(self, titulo, msg):
        self.lblTotal.setText(f"{titulo}: {msg}")

    def mostrar_pedido_confirmado(self, codigo, puntos):
        self.lblTotal.setText(f"Pedido OK #{codigo} (+{puntos} pts)")

    # -------------------------
    # RENDER
    # -------------------------
    def _clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _render(self):
        self._render_header()
        self._render_items()
        self._render_summary()

    def _render_header(self):
        puntos = self._resumen.get("puntos", 0)
        self.lblHeaderPoints.setText(f"⭐ {puntos} pts")

    def _render_items(self):
        self._clear_layout(self.itemsLayout)

        if not self._items:
            lbl = QLabel("Cesta vacía")
            lbl.setStyleSheet("color: white; font-size: 16px; padding: 20px;")
            self.itemsLayout.addWidget(lbl)
            return

        for item in self._items:
            frame = QFrame()
            frame.setStyleSheet(
                "QFrame { background-color: #0A3D5C; border: 2px solid #1A6B9A; "
                "border-radius: 10px; margin: 4px; padding: 8px; }"
            )
            from PyQt5.QtWidgets import QHBoxLayout
            outer = QVBoxLayout(frame)
            outer.setContentsMargins(10, 10, 10, 10)
            outer.setSpacing(6)

            nombre = QLabel(f"🍣  {item['nombre']}")
            nombre.setStyleSheet("color: white; font-size: 15px; font-weight: bold; border: none;")

            fila_precio = QHBoxLayout()
            precio = QLabel(f"{item['precio']:.2f} €" if isinstance(item['precio'], float) else f"{item['precio']} €")
            precio.setStyleSheet("color: #FC814A; font-size: 14px; font-weight: bold; border: none;")
            cantidad_lbl = QLabel(f"Cantidad: {item['cantidad']}")
            cantidad_lbl.setStyleSheet("color: #A0D4F5; font-size: 13px; border: none;")
            fila_precio.addWidget(precio)
            fila_precio.addStretch()
            fila_precio.addWidget(cantidad_lbl)

            fila_botones = QHBoxLayout()
            btn_del = QPushButton("🗑 Eliminar")
            btn_del.setStyleSheet(
                "QPushButton { background-color: #8B0000; color: white; border-radius: 6px; "
                "padding: 4px 10px; font-size: 12px; border: none; }"
                "QPushButton:hover { background-color: #CC0000; }"
            )

            pid = item["id"]
            btn_del.clicked.connect(lambda _, i=pid: self.eliminar_requested.emit(i))

            fila_botones.addStretch()
            fila_botones.addWidget(btn_del)

            outer.addWidget(nombre)
            outer.addLayout(fila_precio)
            outer.addLayout(fila_botones)

            self.itemsLayout.addWidget(frame)

    def _render_summary(self):
        total = self._resumen.get("total", 0)
        puntos = self._resumen.get("puntos", 0)
        desc = self._resumen.get("descuento", 0)

        self.lblTotal.setText(f"{total:.2f} €")
        self.lblPuntos.setText(str(puntos))
        self.lblDescuento.setText(f"-{desc:.2f} €")