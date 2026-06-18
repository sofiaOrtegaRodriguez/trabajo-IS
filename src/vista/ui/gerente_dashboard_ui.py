"""
Vista del dashboard del gerente.
"""

import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget, QFrame, QVBoxLayout, QComboBox, QDateEdit, QPushButton

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.vista.ui.auth_common import C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_DIM, C_TEXT_MUTED


class RevenueCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(6, 3.5), dpi=100, facecolor=C_CREAM)
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)
        if parent is not None:
            self.setParent(parent)

    def draw_data(self, series, title="Ganancias"):
        self.ax.clear()
        self.ax.set_facecolor(C_CREAM)
        if not series:
            self.ax.text(0.5, 0.5, "Sin datos para el rango seleccionado", ha="center", va="center", color="#163246", fontsize=12, fontweight="bold")
            self.ax.set_axis_off()
            self.draw()
            return

        labels = [item["label"] for item in series]
        values = [item["ingresos"] for item in series]
        positions = list(range(len(labels)))
        bars = self.ax.bar(positions, values, color=C_ORANGE, edgecolor=C_ORANGE_DARK, linewidth=1.2)
        self.ax.set_title(title, color="#163246", fontsize=13, fontweight="bold")
        self.ax.set_xticks(positions)
        self.ax.set_xticklabels(labels, rotation=35, ha="right", color="#163246")
        self.ax.tick_params(axis="y", colors="#163246")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color("#D8C8BA")
        self.ax.spines["bottom"].set_color("#D8C8BA")
        self.ax.grid(axis="y", color="#EADFD2", linewidth=0.8, alpha=0.8)
        for bar, value in zip(bars, values):
            self.ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.0f}", ha="center", va="bottom", fontsize=9, color="#163246")
        self.figure.tight_layout(pad=2.0)
        self.draw()


class GerenteDashboardUI(QWidget):
    cerrar_sesion = pyqtSignal()
    filtro_aplicado = pyqtSignal(object, object)
    rango_reseteado = pyqtSignal()
    categoria_cambiada = pyqtSignal(str, bool)

    def __init__(self, sesion, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._sesion = sesion
        self._categorias_opciones = []
        self._load_ui()
        self._wire_signals()

    def _ui_path(self, filename):
        return os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", filename)

    def _load_ui(self):
        self.setWindowTitle("sushUle - Dashboard gerente")
        self.setMinimumSize(1280, 820)
        self.setStyleSheet("background-color: #147DB2;")
        uic.loadUi(self._ui_path("GerenteDashboardUI.ui"), self)

        self.start_date = self._must_get("start_date")
        self.end_date = self._must_get("end_date")
        self.apply_button = self._must_get("apply_button")
        self.reset_button = self._must_get("reset_button")
        self.category_selector = self._must_get("category_selector")
        self.category_order_selector = self._must_get("category_order_selector")
        self.employee_types_box = self._must_get("employee_types_box")
        self.category_summary_label = self._must_get("category_summary_label")
        self.metric_value_labels = {}
        self.metric_subtitle_labels = {}
        self._register_metric_card("pedidos", self._must_get("card_pedidos"))
        self._register_metric_card("clientes", self._must_get("card_clientes"))
        self._register_metric_card("ingresos", self._must_get("card_ingresos"))
        self._register_metric_card("empleados", self._must_get("card_empleados"))
        self.categories_container = self._must_get("categories_container")
        self.categories_layout = self.categories_container.layout()
        self.chart_placeholder = self._must_get("chart_placeholder")
        self.revenue_canvas = RevenueCanvas(self.chart_placeholder)
        if self.chart_placeholder.layout() is not None:
            self.chart_placeholder.layout().addWidget(self.revenue_canvas)

        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setDate(QDate.currentDate().addDays(-29))
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setDate(QDate.currentDate())
        self._must_get("greeting").setText(f"HOLA {getattr(self._sesion, 'nombre', '')}")

    def _wire_signals(self):
        self._must_get("logout_button").clicked.connect(lambda: self.cerrar_sesion.emit())
        self.apply_button.clicked.connect(self._emitir_filtro_aplicado)
        self.reset_button.clicked.connect(self._emitir_rango_reseteado)
        self.category_selector.currentIndexChanged.connect(self._emitir_categoria_cambiada)
        self.category_order_selector.currentIndexChanged.connect(self._emitir_categoria_cambiada)

    def _must_get(self, name):
        widget = getattr(self, name, None)
        if widget is None:
            raise RuntimeError(f"Falta el widget '{name}' en GerenteDashboardUI.ui")
        return widget

    def _register_metric_card(self, key, card):
        labels = card.findChildren(QLabel)
        if len(labels) < 3:
            raise RuntimeError(f"La tarjeta '{key}' no tiene los labels esperados")
        self.metric_value_labels[key] = labels[1]
        self.metric_subtitle_labels[key] = labels[2]

    def _emitir_filtro_aplicado(self, *args):
        self.filtro_aplicado.emit(*self.obtener_rango_fechas())

    def _emitir_rango_reseteado(self):
        self.start_date.setDate(QDate.currentDate().addDays(-29))
        self.end_date.setDate(QDate.currentDate())
        self.rango_reseteado.emit()

    def obtener_rango_fechas(self):
        return self.start_date.date().toPyDate(), self.end_date.date().toPyDate()

    def obtener_categoria_seleccionada(self):
        return self.category_selector.currentText().strip()

    def obtener_orden_desc(self):
        return self.category_order_selector.currentIndex() == 0

    def _emitir_categoria_cambiada(self, *args):
        self.categoria_cambiada.emit(self.obtener_categoria_seleccionada(), self.obtener_orden_desc())

    def inicializar_categorias(self, categorias, seleccion="Todas las categorias"):
        self._categorias_opciones = list(categorias or [])
        opciones = self._categorias_opciones or ["Todas las categorias"]
        current = seleccion if seleccion in opciones else opciones[0]
        self.category_selector.blockSignals(True)
        self.category_selector.clear()
        self.category_selector.addItems(opciones)
        self.category_selector.setCurrentText(current)
        self.category_selector.blockSignals(False)

    def set_resumen(self, resumen, total_empleados):
        self.metric_value_labels["pedidos"].setText(str(resumen["pedidos"]))
        self.metric_subtitle_labels["pedidos"].setText("Pedidos del periodo")
        self.metric_value_labels["clientes"].setText(str(resumen["clientes"]))
        self.metric_subtitle_labels["clientes"].setText("Clientes distintos")
        self.metric_value_labels["ingresos"].setText(f'{resumen["ingresos"]:.2f} €')
        self.metric_subtitle_labels["ingresos"].setText("Ventas totales")
        self.metric_value_labels["empleados"].setText(str(total_empleados))
        self.metric_subtitle_labels["empleados"].setText("Total de empleados")

    def set_grafico(self, series, title):
        self.revenue_canvas.draw_data(series, title)

    def set_empleados_texto(self, texto):
        self.employee_types_box.setText(texto)

    def set_categorias(self, plan):
        self.set_categorias_plan(plan)

    def set_categorias_plan(self, plan):
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.category_summary_label.setText(plan.get("summary", ""))
        bloques = plan.get("bloques", [])
        if not bloques:
            empty = QLabel(plan.get("mensaje", "No hay ventas en las categorias seleccionadas."))
            empty.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            self.categories_layout.addWidget(empty)
            self.categories_layout.addStretch()
            return

        for block in bloques:
            self._add_metric_block(block)
        self.categories_layout.addStretch()

    def _add_metric_block(self, block_data):
        items = list(block_data.get("items", []))
        card_block = QFrame()
        card_block.setStyleSheet("QFrame { background-color: white; border-radius: 18px; }")
        block_layout = QVBoxLayout(card_block)
        block_layout.setContentsMargins(14, 12, 14, 12)
        block_layout.setSpacing(6)

        title = QLabel(block_data["titulo"])
        title.setStyleSheet("color: #163246; font-size: 15px; font-weight: 800;")
        block_layout.addWidget(title)

        if not items:
            empty = QLabel("No hay productos vendidos en esta categoria.")
            empty.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            block_layout.addWidget(empty)
            self.categories_layout.addWidget(card_block)
            return

        for position, item in enumerate(items, start=1):
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #F9F3EB; border-radius: 14px; }")
            item_layout = QVBoxLayout(card)
            item_layout.setContentsMargins(14, 12, 14, 12)
            item_layout.setSpacing(4)
            item_title = QLabel(f"{position}. {item['nombre']}")
            item_title.setStyleSheet("color: #163246; font-size: 15px; font-weight: 800;")
            total_label = QLabel(f"Vendidos: {item['total']}")
            total_label.setStyleSheet("color: #4B6473; font-size: 12px;")
            item_layout.addWidget(item_title)
            item_layout.addWidget(total_label)
            block_layout.addWidget(card)

        self.categories_layout.addWidget(card_block)
