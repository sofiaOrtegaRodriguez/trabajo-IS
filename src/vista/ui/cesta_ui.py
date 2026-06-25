import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal


class CestaUI(QWidget):
    """
    Vista de la cesta de la compra del cliente.

    Muestra los productos añadidos, permite eliminarlos individualmente,
    canjear puntos, finalizar el pedido o abandonar la cesta.

    Patrón MVC: pura VISTA. Los datos llegan desde el controlador a través
    de set_estado() o directamente en el constructor.

    Estructura visual (definida en CestaUI.ui):
      ┌──────────────────────────────────────────┐
      │ [Volver]           ⭐ X pts              │  ← header con puntos
      ├──────────────────────────────────────────┤
      │  ┌──────────────────────────────────┐    │
      │  │ 🍣 Nombre producto               │    │
      │  │ X.XX €              Cantidad: N  │    │  ← itemsLayout (dinámico)
      │  │                    [🗑 Eliminar] │    │
      │  └──────────────────────────────────┘    │
      ├──────────────────────────────────────────┤
      │ Total: X.XX €   Puntos: N   Dto: -X.XX € │  ← resumen
      │ [Canjear]  [Finalizar]  [Abandonar]       │
      └──────────────────────────────────────────┘

    SEÑALES (vista → controlador):
    """

    # Se emite cuando el usuario pulsa "Volver" para regresar a la carta
    volver_carta = pyqtSignal()

    # Se emite cuando el usuario pulsa "Cerrar sesión"
    # (conectada externamente si el .ui tiene ese botón)
    cerrar_sesion = pyqtSignal()

    # Se emite cuando el usuario pulsa "Eliminar" en un item de la cesta.
    # Lleva el id del producto (str) como argumento.
    eliminar_requested = pyqtSignal(str)

    # Se emite cuando el usuario pulsa "Canjear" (usar puntos como descuento)
    canjear_requested = pyqtSignal()

    # Se emite cuando el usuario pulsa "Finalizar" (confirmar el pedido)
    finalizar_requested = pyqtSignal()

    # Se emite cuando el usuario pulsa "Abandonar" (vaciar la cesta y salir)
    abandonar_requested = pyqtSignal()

    # ─────────────────────────────────────────────────────────────
    # CONSTRUCTOR
    # ─────────────────────────────────────────────────────────────

    def __init__(self, items=None, resumen=None, cliente=None):
        super().__init__()

        # Estado interno: datos que se renderizan en la vista
        self._items = items or []        # lista de dicts con nombre, precio, cantidad, id
        self._resumen = resumen or {}    # dict con total, puntos, descuento
        self._cliente = cliente          # VO del cliente (no se usa actualmente en el render)

        # Carga el .ui sobre self: los widgets del .ui quedan como atributos de self
        ui_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ui_pyqt",
            "CestaUI.ui"
        )
        uic.loadUi(ui_path, self)

        # itemsLayout es el QVBoxLayout donde se añaden los frames de cada item dinámicamente.
        # Se obtiene con findChild porque es un layout interno del .ui, no un atributo directo.
        self.itemsLayout = self.findChild(QVBoxLayout, "itemsLayout")

        self._connect_signals()  # conecta botones fijos a sus señales
        self._render()           # renderiza el estado inicial

    # ─────────────────────────────────────────────────────────────
    # CONEXIÓN DE SEÑALES
    # ─────────────────────────────────────────────────────────────

    def _connect_signals(self):
        """
        Conecta los botones fijos del .ui a sus señales correspondientes.
        Los botones de eliminar de cada item se conectan dinámicamente en _render_items().
        """
        self.btnBack.clicked.connect(self.volver_carta)
        self.btnCanjear.clicked.connect(self.canjear_requested)
        self.btnFinalizar.clicked.connect(self.finalizar_requested)
        self.btnAbandonar.clicked.connect(self.abandonar_requested)

    # ─────────────────────────────────────────────────────────────
    # API PÚBLICA: métodos que el controlador llama para actualizar la vista
    # ─────────────────────────────────────────────────────────────

    def set_estado(self, items, resumen, cliente=None):
        """
        Actualiza el estado completo de la cesta y redibuja la vista.
        Es el método principal que llama el controlador cada vez que
        la cesta cambia (al añadir, eliminar o canjear puntos).
        """
        self._items = items
        self._resumen = resumen or {}
        self._cliente = cliente
        self._render()

    def mostrar_mensaje(self, titulo, msg):
        """
        Muestra un mensaje de estado rápido reutilizando el label del total.
        Útil para errores o avisos sin abrir un QMessageBox.
        """
        self.lblTotal.setText(f"{titulo}: {msg}")

    def mostrar_pedido_confirmado(self, codigo, puntos):
        """
        Muestra en el label del total la confirmación del pedido con su código
        y los puntos ganados. Llamado por el controlador tras finalizar con éxito.
        """
        self.lblTotal.setText(f"Pedido OK #{codigo} (+{puntos} pts)")

    # ─────────────────────────────────────────────────────────────
    # RENDERIZADO
    # ─────────────────────────────────────────────────────────────

    def _clear_layout(self, layout):
        """
        Elimina todos los widgets del layout dado, liberando su memoria.
        Mismo patrón que en HistorialUI: takeAt(0) en bucle + deleteLater().
        """
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)   # extrae y elimina el primer item del layout
            widget = item.widget()
            if widget:
                widget.deleteLater()  # destrucción segura en el siguiente ciclo del event loop

    def _render(self):
        """Punto de entrada del renderizado: actualiza las tres secciones de la vista."""
        self._render_header()
        self._render_items()
        self._render_summary()

    def _render_header(self):
        """
        Actualiza el label de puntos en el header.
        Los puntos se leen del resumen, no del VO del cliente, para reflejar
        siempre el estado actual (incluyendo puntos canjeados si aplica).
        """
        puntos = self._resumen.get("puntos", 0)
        self.lblHeaderPoints.setText(f"⭐ {puntos} pts")

    def _render_items(self):
        """
        Genera y añade un QFrame por cada item de la cesta en itemsLayout.

        Cada frame se construye completamente por código (sin .ui propio)
        porque el número de items es dinámico. Estructura por item:
          QFrame
          └── QVBoxLayout (outer)
               ├── QLabel   nombre del producto
               ├── QHBoxLayout (fila_precio)
               │    ├── QLabel  precio
               │    ├── stretch
               │    └── QLabel  cantidad
               └── QHBoxLayout (fila_botones)
                    ├── stretch
                    └── QPushButton  [🗑 Eliminar]

        Si la cesta está vacía, muestra un label "Cesta vacía" en su lugar.
        """
        self._clear_layout(self.itemsLayout)  # limpia items anteriores antes de redibujar

        if not self._items:
            # Caso cesta vacía: muestra mensaje en lugar de la lista
            lbl = QLabel("Cesta vacía")
            lbl.setStyleSheet("color: white; font-size: 16px; padding: 20px;")
            self.itemsLayout.addWidget(lbl)
            return

        for item in self._items:
            # ── Contenedor del item ────────────────────────────────
            frame = QFrame()
            frame.setStyleSheet(
                "QFrame { background-color: #0A3D5C; border: 2px solid #1A6B9A; "
                "border-radius: 10px; margin: 4px; padding: 8px; }"
            )
            from PyQt5.QtWidgets import QHBoxLayout
            outer = QVBoxLayout(frame)
            outer.setContentsMargins(10, 10, 10, 10)
            outer.setSpacing(6)

            # ── Nombre del producto ────────────────────────────────
            nombre = QLabel(f"🍣  {item['nombre']}")
            nombre.setStyleSheet("color: white; font-size: 15px; font-weight: bold; border: none;")

            # ── Fila de precio y cantidad ──────────────────────────
            fila_precio = QHBoxLayout()
            # Formatea el precio con 2 decimales solo si es float
            precio = QLabel(f"{item['precio']:.2f} €" if isinstance(item['precio'], float) else f"{item['precio']} €")
            precio.setStyleSheet("color: #FC814A; font-size: 14px; font-weight: bold; border: none;")
            cantidad_lbl = QLabel(f"Cantidad: {item['cantidad']}")
            cantidad_lbl.setStyleSheet("color: #A0D4F5; font-size: 13px; border: none;")
            fila_precio.addWidget(precio)
            fila_precio.addStretch()     # separa precio (izquierda) de cantidad (derecha)
            fila_precio.addWidget(cantidad_lbl)

            # ── Fila del botón eliminar ────────────────────────────
            fila_botones = QHBoxLayout()
            btn_del = QPushButton("🗑 Eliminar")
            btn_del.setStyleSheet(
                "QPushButton { background-color: #8B0000; color: white; border-radius: 6px; "
                "padding: 4px 10px; font-size: 12px; border: none; }"
                "QPushButton:hover { background-color: #CC0000; }"
            )

            # TRUCO de closures: i=pid captura el id del item en el momento del bucle,
            # evitando que todos los botones emitan el id del último item de la lista
            pid = item["id"]
            btn_del.clicked.connect(lambda _, i=pid: self.eliminar_requested.emit(i))

            fila_botones.addStretch()    # empuja el botón hacia la derecha
            fila_botones.addWidget(btn_del)

            # ── Ensambla el frame ──────────────────────────────────
            outer.addWidget(nombre)
            outer.addLayout(fila_precio)
            outer.addLayout(fila_botones)

            self.itemsLayout.addWidget(frame)

    def _render_summary(self):
        """
        Actualiza los labels del resumen en la parte inferior de la vista:
          - lblTotal:     total a pagar en euros
          - lblPuntos:    puntos acumulados del cliente
          - lblDescuento: descuento aplicado (negativo, por eso el prefijo "-")

        Los valores se leen del dict self._resumen con get() para evitar
        KeyError si algún campo no viene en el dict.
        """
        total = self._resumen.get("total", 0)
        puntos = self._resumen.get("puntos", 0)
        desc = self._resumen.get("descuento", 0)

        self.lblTotal.setText(f"{total:.2f} €")
        self.lblPuntos.setText(str(puntos))
        self.lblDescuento.setText(f"-{desc:.2f} €")