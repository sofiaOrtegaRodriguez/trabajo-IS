import sys
from datetime import date, datetime

import os

from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.controlador.ControladorMetricas import ControladorMetricas
from src.modelo.Logica import Logica
from src.modelo.vo.SesionVo import SesionVo
from src.vista.ui.auth_common import C_BACKGROUND, C_CARD, C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_DIM, C_TEXT_MUTED


class MetricCard(QFrame):
    def __init__(self, title, value="0", subtitle="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {C_CREAM};
                border-radius: 24px;
            }}
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)
        self.title = QLabel(title)
        self.title.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 12px; font-weight: 700;")
        self.value = QLabel(value)
        self.value.setStyleSheet("color: #163246; font-size: 26px; font-weight: 900;")
        self.subtitle = QLabel(subtitle)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.subtitle)

    def set_value(self, value, subtitle=""):
        self.value.setText(str(value))
        if subtitle:
            self.subtitle.setText(subtitle)


class RevenueCanvas(FigureCanvas):
    def __init__(self):
        self.figure = Figure(figsize=(6, 3.5), dpi=100, facecolor=C_CREAM)
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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

    def __init__(self, sesion, controlador=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._sesion = sesion
        self.controlador = controlador or ControladorMetricas(Logica())
        self._build()
        self._load_metrics()

    def _build(self):
        self.setWindowTitle("sushUle - Dashboard gerente")
        self.setMinimumSize(1280, 820)
        self.setStyleSheet(f"background-color: {C_BACKGROUND};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        header = QFrame()
        header.setStyleSheet(
            f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 34px;
            }}
            """
        )
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(26, 24, 26, 24)
        header_layout.setSpacing(10)

        top_row = QHBoxLayout()
        title = QLabel("Dashboard de gerente")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 800;")
        top_row.addWidget(title)
        top_row.addStretch()

        logout_button = QPushButton("Cerrar sesion")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE_DARK};
            }}
            """
        )
        logout_button.clicked.connect(lambda checked=False: self.cerrar_sesion.emit())
        top_row.addWidget(logout_button)
        header_layout.addLayout(top_row)

        greeting = QLabel(f"HOLA {self._sesion.nombre}")
        greeting.setStyleSheet("color: white; font-size: 34px; font-weight: 900;")
        header_layout.addWidget(greeting)

        subtitle = QLabel("Consulta ventas, empleados y productos con filtros por fecha y comparativas mensuales.")
        subtitle.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 14px;")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        root.addWidget(header)

        filter_card = QFrame()
        filter_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {C_CREAM};
                border-radius: 28px;
            }}
            QLabel {{
                color: #163246;
            }}
            QDateEdit {{
                background-color: white;
                border: 1px solid #D8C8BA;
                border-radius: 16px;
                color: #163246;
                font-size: 13px;
                padding: 8px 10px;
            }}
            """
        )
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(18, 14, 18, 14)
        filter_layout.setSpacing(12)

        filter_layout.addWidget(QLabel("Desde"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setDate(QDate.currentDate().addDays(-29))
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("Hasta"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)

        self.apply_button = QPushButton("Aplicar filtro")
        self.apply_button.setCursor(Qt.PointingHandCursor)
        self.apply_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 13px;
                font-weight: 700;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE_DARK};
            }}
            """
        )
        self.apply_button.clicked.connect(self._load_metrics)
        filter_layout.addWidget(self.apply_button)

        self.reset_button = QPushButton("Ultimos 30 dias")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_CREAM};
                color: #163246;
                border: 1px solid #D8C8BA;
                border-radius: 16px;
                font-size: 13px;
                font-weight: 700;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: #F3E6D8;
            }}
            """
        )
        self.reset_button.clicked.connect(self._reset_range)
        filter_layout.addWidget(self.reset_button)
        filter_layout.addStretch()
        root.addWidget(filter_card)

        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(14)
        self.metric_cards = {
            "pedidos": MetricCard("Pedidos", "0", "Pedidos dentro del rango"),
            "clientes": MetricCard("Clientes", "0", "Clientes con pedidos"),
            "ingresos": MetricCard("Ingresos", "0 €", "Ventas totales"),
            "empleados": MetricCard("Empleados", "0", "Plantilla total"),
        }
        for card in self.metric_cards.values():
            self.cards_row.addWidget(card, 1)
        root.addLayout(self.cards_row)

        content_area = QHBoxLayout()
        content_area.setSpacing(18)

        left_column = QVBoxLayout()
        left_column.setSpacing(18)

        chart_card = QFrame()
        chart_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {C_CREAM};
                border-radius: 28px;
            }}
            """
        )
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(18, 18, 18, 18)
        chart_layout.setSpacing(10)
        chart_title = QLabel("Comparativa de ganancias por mes")
        chart_title.setStyleSheet("color: #163246; font-size: 18px; font-weight: 800;")
        chart_layout.addWidget(chart_title)
        self.revenue_canvas = RevenueCanvas()
        chart_layout.addWidget(self.revenue_canvas, 1)
        left_column.addWidget(chart_card, 2)

        employees_card = QFrame()
        employees_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {C_CREAM};
                border-radius: 28px;
            }}
            """
        )
        emp_layout = QVBoxLayout(employees_card)
        emp_layout.setContentsMargins(18, 18, 18, 18)
        emp_layout.setSpacing(10)
        emp_title = QLabel("Empleados por tipo")
        emp_title.setStyleSheet("color: #163246; font-size: 18px; font-weight: 800;")
        emp_layout.addWidget(emp_title)
        self.employee_types_box = QLabel("")
        self.employee_types_box.setWordWrap(True)
        self.employee_types_box.setStyleSheet("color: #163246; font-size: 13px;")
        emp_layout.addWidget(self.employee_types_box)
        left_column.addWidget(employees_card, 1)

        content_area.addLayout(left_column, 5)

        right_column = QVBoxLayout()
        right_column.setSpacing(18)

        products_card = QFrame()
        products_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {C_CREAM};
                border-radius: 28px;
            }}
            """
        )
        products_layout = QVBoxLayout(products_card)
        products_layout.setContentsMargins(18, 18, 18, 18)
        products_layout.setSpacing(10)
        products_title = QLabel("Productos por categoria")
        products_title.setStyleSheet("color: #163246; font-size: 18px; font-weight: 800;")
        products_layout.addWidget(products_title)

        selector_row = QHBoxLayout()
        selector_row.setSpacing(10)
        selector_label = QLabel("Categoria")
        selector_label.setStyleSheet("color: #163246; font-size: 12px; font-weight: 700;")
        selector_row.addWidget(selector_label)
        self.category_selector = QComboBox()
        self.category_selector.addItem("Todas las categorias")
        self.category_selector.currentIndexChanged.connect(self._render_selected_category)
        selector_row.addWidget(self.category_selector, 1)
        order_label = QLabel("Orden")
        order_label.setStyleSheet("color: #163246; font-size: 12px; font-weight: 700;")
        selector_row.addWidget(order_label)
        self.category_order_selector = QComboBox()
        self.category_order_selector.addItems(["Mas vendidos", "Menos vendidos"])
        self.category_order_selector.currentIndexChanged.connect(self._render_selected_category)
        selector_row.addWidget(self.category_order_selector, 1)
        products_layout.addLayout(selector_row)

        self.categories_scroll = QScrollArea()
        self.categories_scroll.setWidgetResizable(True)
        self.categories_scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        self.categories_container = QWidget()
        self.categories_container.setStyleSheet("background:transparent;")
        self.categories_layout = QVBoxLayout(self.categories_container)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)
        self.categories_layout.setSpacing(10)
        self.categories_layout.addStretch()
        self.categories_scroll.setWidget(self.categories_container)
        products_layout.addWidget(self.categories_scroll, 1)
        self.category_summary_label = QLabel("")
        self.category_summary_label.setWordWrap(True)
        self.category_summary_label.setStyleSheet("color: #163246; font-size: 12px;")
        products_layout.addWidget(self.category_summary_label)
        right_column.addWidget(products_card, 1)

        content_area.addLayout(right_column, 4)
        root.addLayout(content_area, 1)

    def _reset_range(self):
        self.start_date.setDate(QDate.currentDate().addDays(-29))
        self.end_date.setDate(QDate.currentDate())
        self._load_metrics()

    def _load_metrics(self):
        try:
            fecha_inicio = self.start_date.date().toPyDate()
            fecha_fin = self.end_date.date().toPyDate()
            data = self.controlador.obtener_metricas(fecha_inicio, fecha_fin)
        except Exception as exc:
            QMessageBox.warning(self, "Metricas", str(exc))
            return

        resumen = data["resumen"]
        empleados = data["empleados"]
        categorias = data["categorias"]
        mensuales = data["mensuales"]
        diarios = data["diarios"]

        self.metric_cards["pedidos"].set_value(resumen["pedidos"], "Pedidos del periodo")
        self.metric_cards["clientes"].set_value(resumen["clientes"], "Clientes distintos")
        self.metric_cards["ingresos"].set_value(f'{resumen["ingresos"]:.2f} €', "Ventas totales")
        total_empleados = sum(item["total"] for item in empleados)
        self.metric_cards["empleados"].set_value(total_empleados, "Total de empleados")

        self._category_data = categorias
        self._refresh_category_selector()

        if empleados:
            labels = [f'{item["tipo"]}: {item["total"]}' for item in empleados]
            self.employee_types_box.setText("\n".join(labels))
        else:
            self.employee_types_box.setText("Todavia no hay empleados cargados.")

        days_selected = (self.end_date.date().toPyDate() - self.start_date.date().toPyDate()).days
        if days_selected <= 31:
            self.revenue_canvas.draw_data(diarios, "Ganancias diarias")
        else:
            self.revenue_canvas.draw_data(mensuales, "Ganancias por mes")
        self._render_selected_category()

    def _refresh_category_selector(self):
        current = self.category_selector.currentText()
        self.category_selector.blockSignals(True)
        self.category_selector.clear()
        self.category_selector.addItem("Todas las categorias")
        categories = [item["categoria"] for item in getattr(self, "_category_data", [])]
        self.category_selector.addItems(categories)
        if current and current in ("Todas las categorias", *categories):
            self.category_selector.setCurrentText(current)
        elif categories:
            self.category_selector.setCurrentIndex(0)
        self.category_selector.blockSignals(False)

    def _render_selected_category(self):
        categorias = getattr(self, "_category_data", [])
        selected = self.category_selector.currentText().strip()
        order_desc = self.category_order_selector.currentIndex() == 0

        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        if not categorias or not selected:
            empty = QLabel("No hay ventas en las categorias seleccionadas.")
            empty.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            self.categories_layout.addWidget(empty)
            self.categories_layout.addStretch()
            self.category_summary_label.setText("")
            return

        if selected == "Todas las categorias":
            self.category_summary_label.setText("Mostrando todos los productos.")
            flat_items = []
            for category in categorias:
                for item in category["items"]:
                    flat_items.append(
                        {
                            "nombre": item["nombre"],
                            "total": item["total"],
                            "categoria": category["categoria"],
                        }
                    )
            flat_items.sort(key=lambda item: (item["total"], item["nombre"]), reverse=order_desc)
            self._add_flat_products_block("Todos los productos", flat_items, order_desc)
            self.categories_layout.addStretch()
            return

        category = next((item for item in categorias if item["categoria"] == selected), None)
        if category is None:
            empty = QLabel("No hay ventas en la categoria seleccionada.")
            empty.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            self.categories_layout.addWidget(empty)
            self.categories_layout.addStretch()
            self.category_summary_label.setText("")
            return

        self.category_summary_label.setText(
            f"Mostrando {'mas vendidos' if order_desc else 'menos vendidos'} de {category['categoria']}."
        )
        self._add_category_block(category, order_desc)
        self.categories_layout.addStretch()

    def _add_category_block(self, category, order_desc):
        items = list(category["items"])
        items.sort(key=lambda item: (item["total"], item["nombre"]), reverse=order_desc)

        block = QFrame()
        block.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 18px;
            }
            """
        )
        layout = QVBoxLayout(block)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title = QLabel(category["categoria"])
        title.setStyleSheet("color: #163246; font-size: 15px; font-weight: 800;")
        layout.addWidget(title)

        if not items:
            empty = QLabel("No hay productos vendidos en esta categoria.")
            empty.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            layout.addWidget(empty)
            self.categories_layout.addWidget(block)
            return

        for position, item in enumerate(items, start=1):
            card = QFrame()
            card.setStyleSheet(
                """
                QFrame {
                    background-color: #F9F3EB;
                    border-radius: 14px;
                }
                """
            )
            item_layout = QVBoxLayout(card)
            item_layout.setContentsMargins(14, 12, 14, 12)
            item_layout.setSpacing(4)
            item_title = QLabel(f"{position}. {item['nombre']}")
            item_title.setStyleSheet("color: #163246; font-size: 15px; font-weight: 800;")
            total_label = QLabel(f"Vendidos: {item['total']}")
            total_label.setStyleSheet("color: #4B6473; font-size: 12px;")
            item_layout.addWidget(item_title)
            item_layout.addWidget(total_label)
            block_layout = block.layout()
            if block_layout is not None:
                block_layout.addWidget(card)

        self.categories_layout.addWidget(block)

    def _add_flat_products_block(self, title_text, items, order_desc):
        block = QFrame()
        block.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 18px;
            }
            """
        )
        block_layout = QVBoxLayout(block)
        block_layout.setContentsMargins(14, 12, 14, 12)
        block_layout.setSpacing(6)

        title = QLabel(title_text)
        title.setStyleSheet("color: #163246; font-size: 15px; font-weight: 800;")
        block_layout.addWidget(title)

        if not items:
            empty = QLabel("No hay productos vendidos en el rango seleccionado.")
            empty.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            block_layout.addWidget(empty)
            self.categories_layout.addWidget(block)
            return

        for position, item in enumerate(items, start=1):
            card = QFrame()
            card.setStyleSheet(
                """
                QFrame {
                    background-color: #F9F3EB;
                    border-radius: 14px;
                }
                """
            )
            item_layout = QVBoxLayout(card)
            item_layout.setContentsMargins(14, 12, 14, 12)
            item_layout.setSpacing(4)

            item_title = QLabel(f"{position}. {item['nombre']}")
            item_title.setStyleSheet("color: #163246; font-size: 15px; font-weight: 800;")
            total_label = QLabel(f"Vendidos: {item['total']}")
            total_label.setStyleSheet("color: #4B6473; font-size: 12px;")
            category_label = QLabel(f"Categoria: {item['categoria']}")
            category_label.setStyleSheet("color: #7B97A5; font-size: 11px;")

            item_layout.addWidget(item_title)
            item_layout.addWidget(total_label)
            item_layout.addWidget(category_label)
            block_layout.addWidget(card)

        self.categories_layout.addWidget(block)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sesion_demo = SesionVo(0, "Gerente", "gerente@sushule.local", 0, None, "gerente")
    window = GerenteDashboardUI(sesion_demo)
    window.show()
    sys.exit(app.exec_())
