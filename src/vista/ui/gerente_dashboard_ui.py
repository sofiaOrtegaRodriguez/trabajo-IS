"""
Vista del dashboard del gerente.

Esta pantalla muestra métricas y gráficos de rendimiento del restaurante.
El gerente puede filtrar por rango de fechas y categorías de productos.

Patrón MVC: pura VISTA. Toda acción del usuario se comunica al controlador
mediante señales (pyqtSignal). El controlador llama a los métodos públicos
de esta clase para actualizar los datos mostrados.
"""

import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget, QFrame, QVBoxLayout, QComboBox, QDateEdit, QPushButton

# Arreglo para ejecución directa o como módulo importado
if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

# Matplotlib integrado en PyQt5: FigureCanvas es el widget que contiene el gráfico
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Constantes de color compartidas con el resto de la app
from src.vista.ui.auth_common import C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_DIM, C_TEXT_MUTED


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENTE AUXILIAR: gráfico de barras de ingresos
# ─────────────────────────────────────────────────────────────────────────────

class RevenueCanvas(FigureCanvas):
    """
    Widget de matplotlib embebido en PyQt5 que muestra un gráfico de barras
    con los ingresos por periodo (día, semana, mes, etc.).

    Hereda de FigureCanvas, que a su vez hereda de QWidget, por lo que puede
    insertarse directamente en cualquier layout de PyQt5.
    """

    def __init__(self, parent=None):
        # Crea la figura de matplotlib con fondo crema para que encaje con el estilo de la app
        self.figure = Figure(figsize=(6, 3.5), dpi=100, facecolor=C_CREAM)
        self.ax = self.figure.add_subplot(111)  # único subplot (1 fila, 1 col, posición 1)
        super().__init__(self.figure)
        if parent is not None:
            self.setParent(parent)

    def draw_data(self, series, title="Ganancias"):
        """
        Redibuja el gráfico con los datos recibidos.

        Parámetros:
          series: lista de dicts con claves "label" (eje X) e "ingresos" (valor Y)
          title:  título del gráfico (p.ej. "Ganancias por día")

        Si series está vacío, muestra un mensaje de "Sin datos" en lugar del gráfico.
        """
        self.ax.clear()  # borra el gráfico anterior antes de redibujar
        self.ax.set_facecolor(C_CREAM)

        # Caso sin datos: muestra texto centrado y oculta los ejes
        if not series:
            self.ax.text(
                0.5, 0.5,
                "Sin datos para el rango seleccionado",
                ha="center", va="center",
                color="#163246", fontsize=12, fontweight="bold"
            )
            self.ax.set_axis_off()
            self.draw()
            return

        # Extrae etiquetas y valores de la serie
        labels = [item["label"] for item in series]
        values = [item["ingresos"] for item in series]
        positions = list(range(len(labels)))  # posiciones numéricas para las barras

        # Dibuja las barras con color naranja de la app
        bars = self.ax.bar(positions, values, color=C_ORANGE, edgecolor=C_ORANGE_DARK, linewidth=1.2)

        # Estilo del gráfico: título, ejes, cuadrícula
        self.ax.set_title(title, color="#163246", fontsize=13, fontweight="bold")
        self.ax.set_xticks(positions)
        self.ax.set_xticklabels(labels, rotation=35, ha="right", color="#163246")
        self.ax.tick_params(axis="y", colors="#163246")
        self.ax.spines["top"].set_visible(False)     # oculta borde superior
        self.ax.spines["right"].set_visible(False)   # oculta borde derecho
        self.ax.spines["left"].set_color("#D8C8BA")
        self.ax.spines["bottom"].set_color("#D8C8BA")
        self.ax.grid(axis="y", color="#EADFD2", linewidth=0.8, alpha=0.8)

        # Etiqueta de valor encima de cada barra
        for bar, value in zip(bars, values):
            self.ax.text(
                bar.get_x() + bar.get_width() / 2,  # centrado horizontalmente en la barra
                bar.get_height(),                    # justo encima de la barra
                f"{value:.0f}",
                ha="center", va="bottom", fontsize=9, color="#163246"
            )

        self.figure.tight_layout(pad=2.0)  # ajusta márgenes para que no se recorten las etiquetas
        self.draw()  # renderiza el gráfico en el canvas de PyQt5


# ─────────────────────────────────────────────────────────────────────────────
# VISTA PRINCIPAL: dashboard del gerente
# ─────────────────────────────────────────────────────────────────────────────

class GerenteDashboardUI(QWidget):
    """
    Pantalla principal del gerente. Estructura visual (definida en el .ui):

    ┌──────────────────────────────────────────────────────────────────┐
    │  Saludo + botón cerrar sesión                                    │
    ├──────────────────────────────────────────────────────────────────┤
    │  Filtros: [fecha inicio] [fecha fin] [Aplicar] [Resetear]       │
    ├────────────────┬─────────────────────────────────────────────────┤
    │ Tarjetas       │  Selector categoría + orden                     │
    │ métricas:      │  ────────────────────────────────────────────── │
    │  · Pedidos     │  Gráfico de barras de ingresos (RevenueCanvas)  │
    │  · Clientes    │  ────────────────────────────────────────────── │
    │  · Ingresos    │  Bloques de ranking de productos por categoría  │
    │  · Empleados   │                                                 │
    └────────────────┴─────────────────────────────────────────────────┘

    SEÑALES (vista → controlador):
    """

    # Se emite cuando el usuario pulsa "Cerrar sesión"
    cerrar_sesion = pyqtSignal()

    # Se emite cuando el usuario pulsa "Aplicar filtro".
    # Lleva dos argumentos: fecha_inicio y fecha_fin (datetime.date)
    filtro_aplicado = pyqtSignal(object, object)

    # Se emite cuando el usuario pulsa "Resetear rango"
    rango_reseteado = pyqtSignal()

    # Se emite cuando el usuario cambia la categoría seleccionada o el orden.
    # Lleva: nombre_categoria (str) y orden_descendente (bool)
    categoria_cambiada = pyqtSignal(str, bool)

    # ─────────────────────────────────────────────────────────────────
    # CONSTRUCTOR
    # ─────────────────────────────────────────────────────────────────

    def __init__(self, sesion, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)  # libera memoria al cerrar
        self._sesion = sesion                          # VO de sesión (para mostrar nombre del gerente)
        self._categorias_opciones = []                 # lista de categorías disponibles
        self._load_ui()       # 1. construye la interfaz
        self._wire_signals()  # 2. conecta botones y selectores a sus emisores de señal

    # ─────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────

    def _ui_path(self, filename):
        """Devuelve la ruta absoluta del archivo .ui dado su nombre."""
        return os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", filename)

    def _must_get(self, name):
        """
        Obtiene un atributo del widget (inyectado por uic.loadUi) por nombre.
        Lanza RuntimeError si no existe, para detectar errores del .ui en el arranque.

        Uso: self.apply_button = self._must_get("apply_button")
        """
        widget = getattr(self, name, None)
        if widget is None:
            raise RuntimeError(f"Falta el widget '{name}' en GerenteDashboardUI.ui")
        return widget

    # ─────────────────────────────────────────────────────────────────
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ─────────────────────────────────────────────────────────────────

    def _load_ui(self):
        """
        Carga el archivo .ui y obtiene referencias a todos los widgets
        que se necesitarán después.

        También configura valores por defecto de los campos de fecha
        y crea el RevenueCanvas (gráfico de matplotlib) dentro del
        placeholder reservado en el .ui.
        """
        self.setWindowTitle("sushUle - Dashboard gerente")
        self.setMinimumSize(1280, 820)
        self.setStyleSheet("background-color: #147DB2;")

        # Carga el .ui sobre self: todos los widgets del .ui quedan como atributos de self
        uic.loadUi(self._ui_path("GerenteDashboardUI.ui"), self)

        # ── Referencias a widgets de filtros ────────────────────────
        self.start_date = self._must_get("start_date")                     # QDateEdit: fecha inicio
        self.end_date = self._must_get("end_date")                         # QDateEdit: fecha fin
        self.apply_button = self._must_get("apply_button")                 # QPushButton: aplicar filtro
        self.reset_button = self._must_get("reset_button")                 # QPushButton: resetear
        self.category_selector = self._must_get("category_selector")       # QComboBox: categoría
        self.category_order_selector = self._must_get("category_order_selector")  # QComboBox: orden asc/desc
        self.employee_types_box = self._must_get("employee_types_box")     # QLabel: resumen de empleados
        self.category_summary_label = self._must_get("category_summary_label")    # QLabel: resumen categoría

        # ── Tarjetas de métricas ─────────────────────────────────────
        # Cada tarjeta tiene 3 QLabel: icono/título, valor numérico, subtítulo.
        # _register_metric_card extrae y guarda los labels [1] y [2] de cada tarjeta.
        self.metric_value_labels = {}     # dict key → QLabel del valor principal
        self.metric_subtitle_labels = {}  # dict key → QLabel del subtítulo descriptivo
        self._register_metric_card("pedidos", self._must_get("card_pedidos"))
        self._register_metric_card("clientes", self._must_get("card_clientes"))
        self._register_metric_card("ingresos", self._must_get("card_ingresos"))
        self._register_metric_card("empleados", self._must_get("card_empleados"))

        # ── Área de categorías (ranking de productos) ────────────────
        self.categories_container = self._must_get("categories_container")
        self.categories_layout = self.categories_container.layout()  # layout donde se añaden los bloques

        # ── Gráfico de ingresos ──────────────────────────────────────
        # chart_placeholder es un QFrame vacío del .ui que actúa como contenedor.
        # Se inserta el RevenueCanvas (widget de matplotlib) dentro de su layout.
        self.chart_placeholder = self._must_get("chart_placeholder")
        self.revenue_canvas = RevenueCanvas(self.chart_placeholder)
        if self.chart_placeholder.layout() is not None:
            self.chart_placeholder.layout().addWidget(self.revenue_canvas)

        # ── Configuración de los campos de fecha ─────────────────────
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setDate(QDate.currentDate().addDays(-29))  # por defecto: últimos 30 días

        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setDate(QDate.currentDate())                  # por defecto: hoy

        # Muestra el nombre del gerente en el saludo
        self._must_get("greeting").setText(f"HOLA {getattr(self._sesion, 'nombre', '')}")

    def _register_metric_card(self, key, card):
        """
        Extrae los QLabel de valor y subtítulo de una tarjeta de métrica
        y los guarda en los dicts metric_value_labels y metric_subtitle_labels.

        Cada tarjeta tiene exactamente 3 QLabel (findChildren los devuelve en orden):
          [0] → label de título/icono (no se usa aquí)
          [1] → label del valor numérico grande  ← se guarda en metric_value_labels[key]
          [2] → label del subtítulo descriptivo  ← se guarda en metric_subtitle_labels[key]

        Lanza RuntimeError si la tarjeta no tiene los 3 labels esperados.
        """
        labels = card.findChildren(QLabel)
        if len(labels) < 3:
            raise RuntimeError(f"La tarjeta '{key}' no tiene los labels esperados")
        self.metric_value_labels[key] = labels[1]
        self.metric_subtitle_labels[key] = labels[2]

    # ─────────────────────────────────────────────────────────────────
    # CONEXIÓN DE SEÑALES INTERNAS
    # ─────────────────────────────────────────────────────────────────

    def _wire_signals(self):
        """
        Conecta los eventos de los widgets a los métodos internos
        que emiten las señales hacia el controlador.
        """
        self._must_get("logout_button").clicked.connect(lambda: self.cerrar_sesion.emit())

        # Botones de filtro de fechas
        self.apply_button.clicked.connect(self._emitir_filtro_aplicado)
        self.reset_button.clicked.connect(self._emitir_rango_reseteado)

        # Cualquier cambio en el selector de categoría o de orden redibuja el ranking
        self.category_selector.currentIndexChanged.connect(self._emitir_categoria_cambiada)
        self.category_order_selector.currentIndexChanged.connect(self._emitir_categoria_cambiada)

    # ─────────────────────────────────────────────────────────────────
    # EMISIÓN DE SEÑALES (vista → controlador)
    # ─────────────────────────────────────────────────────────────────

    def _emitir_filtro_aplicado(self, *args):
        """
        Lee el rango de fechas actual y emite filtro_aplicado con
        (fecha_inicio, fecha_fin) como datetime.date.
        """
        self.filtro_aplicado.emit(*self.obtener_rango_fechas())

    def _emitir_rango_reseteado(self):
        """
        Restablece los campos de fecha a los últimos 30 días
        y emite rango_reseteado para que el controlador recargue los datos.
        """
        self.start_date.setDate(QDate.currentDate().addDays(-29))
        self.end_date.setDate(QDate.currentDate())
        self.rango_reseteado.emit()

    def _emitir_categoria_cambiada(self, *args):
        """
        Lee la categoría y el orden actuales y emite categoria_cambiada.
        Se dispara tanto al cambiar el selector de categoría como el de orden.
        """
        self.categoria_cambiada.emit(
            self.obtener_categoria_seleccionada(),
            self.obtener_orden_desc()
        )

    # ─────────────────────────────────────────────────────────────────
    # GETTERS DE ESTADO (usados internamente y por el controlador)
    # ─────────────────────────────────────────────────────────────────

    def obtener_rango_fechas(self):
        """Devuelve (fecha_inicio, fecha_fin) como tupla de datetime.date."""
        return self.start_date.date().toPyDate(), self.end_date.date().toPyDate()

    def obtener_categoria_seleccionada(self):
        """Devuelve el texto de la categoría seleccionada actualmente (str)."""
        return self.category_selector.currentText().strip()

    def obtener_orden_desc(self):
        """
        Devuelve True si el orden es descendente (mayor a menor).
        El índice 0 del category_order_selector corresponde a orden descendente.
        """
        return self.category_order_selector.currentIndex() == 0

    # ─────────────────────────────────────────────────────────────────
    # API PÚBLICA: métodos que el CONTROLADOR llama para actualizar la vista
    # ─────────────────────────────────────────────────────────────────

    def inicializar_categorias(self, categorias, seleccion="Todas las categorias"):
        """
        Rellena el combobox de categorías con la lista recibida.
        Preserva la selección indicada si existe en la lista.

        Bloquea señales durante la actualización para evitar disparar
        categoria_cambiada mientras se rellena el combobox.
        """
        self._categorias_opciones = list(categorias or [])
        opciones = self._categorias_opciones or ["Todas las categorias"]
        current = seleccion if seleccion in opciones else opciones[0]

        self.category_selector.blockSignals(True)
        self.category_selector.clear()
        self.category_selector.addItems(opciones)
        self.category_selector.setCurrentText(current)
        self.category_selector.blockSignals(False)

    def set_resumen(self, resumen, total_empleados):
        """
        Actualiza las 4 tarjetas de métricas con los datos del periodo.

        Parámetros:
          resumen: dict con claves "pedidos", "clientes", "ingresos"
          total_empleados: int con el número total de empleados activos
        """
        self.metric_value_labels["pedidos"].setText(str(resumen["pedidos"]))
        self.metric_subtitle_labels["pedidos"].setText("Pedidos del periodo")

        self.metric_value_labels["clientes"].setText(str(resumen["clientes"]))
        self.metric_subtitle_labels["clientes"].setText("Clientes distintos")

        self.metric_value_labels["ingresos"].setText(f'{resumen["ingresos"]:.2f} €')
        self.metric_subtitle_labels["ingresos"].setText("Ventas totales")

        self.metric_value_labels["empleados"].setText(str(total_empleados))
        self.metric_subtitle_labels["empleados"].setText("Total de empleados")

    def set_grafico(self, series, title):
        """
        Actualiza el gráfico de barras de ingresos.

        Parámetros:
          series: lista de dicts con "label" e "ingresos"
          title:  título del gráfico
        """
        self.revenue_canvas.draw_data(series, title)

    def set_empleados_texto(self, texto):
        """
        Actualiza el texto del resumen de tipos de empleados
        (p.ej. "3 cocineros, 2 camareros, 1 admin").
        """
        self.employee_types_box.setText(texto)

    def set_categorias(self, plan):
        """
        Punto de entrada para actualizar el panel de ranking de categorías.
        Delega en set_categorias_plan (separado por si en el futuro se añaden
        más tipos de plan).
        """
        self.set_categorias_plan(plan)

    def set_categorias_plan(self, plan):
        """
        Reconstruye el panel de ranking de productos por categoría.

        Parámetro plan (dict):
          "summary":  texto resumen que se muestra arriba del panel
          "bloques":  lista de bloques, cada uno con su propio ranking
          "mensaje":  texto a mostrar si no hay bloques (lista vacía)

        Primero elimina todos los widgets anteriores del layout,
        luego añade los nuevos bloques o un mensaje de vacío.
        """
        # Limpia el panel eliminando todos los widgets anteriores
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # libera memoria del widget eliminado

        # Muestra el texto resumen (p.ej. "Top 3 de Entrantes y Postres")
        self.category_summary_label.setText(plan.get("summary", ""))

        bloques = plan.get("bloques", [])

        # Si no hay datos: muestra un mensaje y añade stretch para empujar hacia arriba
        if not bloques:
            empty = QLabel(plan.get("mensaje", "No hay ventas en las categorias seleccionadas."))
            empty.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            self.categories_layout.addWidget(empty)
            self.categories_layout.addStretch()
            return

        # Añade un bloque por cada categoría
        for block in bloques:
            self._add_metric_block(block)

        # Stretch al final para que los bloques queden pegados arriba
        self.categories_layout.addStretch()

    def _add_metric_block(self, block_data):
        """
        Crea y añade al panel un bloque de ranking para una categoría.

        Estructura visual de un bloque:
          ┌─────────────────────────────┐  ← card_block (fondo blanco)
          │ Título de la categoría      │
          │  ┌───────────────────────┐  │
          │  │ 1. Nombre producto    │  │  ← card por producto (fondo crema)
          │  │    Vendidos: X        │  │
          │  └───────────────────────┘  │
          │  ┌───────────────────────┐  │
          │  │ 2. Nombre producto    │  │
          │  │    Vendidos: X        │  │
          │  └───────────────────────┘  │
          └─────────────────────────────┘

        Parámetro block_data (dict):
          "titulo": nombre de la categoría
          "items":  lista de dicts con "nombre" y "total"
        """
        items = list(block_data.get("items", []))

        # Contenedor del bloque (fondo blanco redondeado)
        card_block = QFrame()
        card_block.setStyleSheet("QFrame { background-color: white; border-radius: 18px; }")
        block_layout = QVBoxLayout(card_block)
        block_layout.setContentsMargins(14, 12, 14, 12)
        block_layout.setSpacing(6)

        # Título de la categoría
        title = QLabel(block_data["titulo"])
        title.setStyleSheet("color: #163246; font-size: 15px; font-weight: 800;")
        block_layout.addWidget(title)

        # Si no hay productos vendidos en esta categoría, muestra aviso y sale
        if not items:
            empty = QLabel("No hay productos vendidos en esta categoria.")
            empty.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            block_layout.addWidget(empty)
            self.categories_layout.addWidget(card_block)
            return

        # Una mini-card por cada producto del ranking
        for position, item in enumerate(items, start=1):  # start=1 para mostrar "1.", "2.", etc.
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #F9F3EB; border-radius: 14px; }")
            item_layout = QVBoxLayout(card)
            item_layout.setContentsMargins(14, 12, 14, 12)
            item_layout.setSpacing(4)

            # Nombre del producto con su posición en el ranking
            item_title = QLabel(f"{position}. {item['nombre']}")
            item_title.setStyleSheet("color: #163246; font-size: 15px; font-weight: 800;")

            # Total de unidades vendidas
            total_label = QLabel(f"Vendidos: {item['total']}")
            total_label.setStyleSheet("color: #4B6473; font-size: 12px;")

            item_layout.addWidget(item_title)
            item_layout.addWidget(total_label)
            block_layout.addWidget(card)

        # Añade el bloque completo al panel de categorías
        self.categories_layout.addWidget(card_block)