"""
Vista de la Cesta — PyQt5, conectada a SQL Server via ServicioCesta.
"""
import sys, os
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox, QDialog, QSizePolicy,
)

C_BG      = "#147DB2"
C_DARK    = "#072D44"
C_CARD    = "#5CA9D0"
C_ORANGE  = "#FC814A"
C_ORANGE_D= "#E66E3A"
C_CREAM   = "#FEF5ED"
C_WHITE   = "#FFFFFF"
C_GREEN   = "#43A047"
C_RED     = "#E53935"
C_MUTED   = "#B6D5E2"


def _btn(text, color, parent=None, min_h=44):
    b = QPushButton(text, parent)
    b.setMinimumHeight(min_h)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton{{background:{color};color:white;border:none;
                     border-radius:22px;font-size:14px;font-weight:700;padding:0 16px;}}
        QPushButton:hover{{background:#555;}}
    """)
    return b


class ConfirmDialog(QDialog):
    def __init__(self, titulo, mensaje, parent=None, color_ok=C_GREEN):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.resultado = False
        self.setStyleSheet(f"background:{C_DARK};border:2px solid {C_ORANGE};border-radius:20px;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 20)
        lay.setSpacing(12)
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet(f"color:white;font-size:16px;font-weight:700;")
        lbl_t.setAlignment(Qt.AlignCenter)
        lbl_m = QLabel(mensaje)
        lbl_m.setStyleSheet(f"color:{C_MUTED};font-size:13px;")
        lbl_m.setAlignment(Qt.AlignCenter)
        lbl_m.setWordWrap(True)
        row = QHBoxLayout()
        btn_cancel = _btn("Cancelar", "#607D8B")
        btn_ok     = _btn("Confirmar", color_ok)
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self._confirmar)
        row.addWidget(btn_cancel)
        row.addWidget(btn_ok)
        lay.addWidget(lbl_t)
        lay.addWidget(lbl_m)
        lay.addLayout(row)
        self.setFixedSize(380, 200)

    def _confirmar(self):
        self.resultado = True
        self.accept()


class PedidoConfirmadoDialog(QDialog):
    def __init__(self, codigo, pts_ganados, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.accion = None
        self.setStyleSheet(f"background:{C_DARK};border:2px solid {C_ORANGE};border-radius:20px;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 24)
        lay.setSpacing(16)

        lbl_t = QLabel("¡Pedido confirmado! 🎉")
        lbl_t.setStyleSheet("color:white;font-size:18px;font-weight:800;")
        lbl_t.setAlignment(Qt.AlignCenter)

        lbl_id = QLabel(f"Tu ID de pedido es:")
        lbl_id.setStyleSheet(f"color:{C_MUTED};font-size:13px;")
        lbl_id.setAlignment(Qt.AlignCenter)

        lbl_codigo = QLabel(str(codigo))
        lbl_codigo.setStyleSheet(f"color:{C_ORANGE};font-size:28px;font-weight:800;")
        lbl_codigo.setAlignment(Qt.AlignCenter)

        lbl_info = QLabel("Acude al cajero con este ID para pagar.")
        lbl_info.setStyleSheet(f"color:{C_MUTED};font-size:12px;")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setWordWrap(True)

        lbl_pts = QLabel(f"⭐ Has ganado {pts_ganados} puntos")
        lbl_pts.setStyleSheet(f"color:{C_ORANGE};font-size:13px;font-weight:700;")
        lbl_pts.setAlignment(Qt.AlignCenter)

        row = QHBoxLayout()
        row.setSpacing(12)
        btn_seguir = _btn("🛒  Seguir pidiendo", C_BG)
        btn_salir  = _btn("🚪  Cerrar sesión",   C_ORANGE)
        btn_seguir.clicked.connect(self._seguir)
        btn_salir.clicked.connect(self._salir)
        row.addWidget(btn_seguir)
        row.addWidget(btn_salir)

        lay.addWidget(lbl_t)
        lay.addWidget(lbl_id)
        lay.addWidget(lbl_codigo)
        lay.addWidget(lbl_info)
        lay.addWidget(lbl_pts)
        lay.addLayout(row)
        self.setFixedSize(420, 300)

    def _seguir(self):
        self.accion = "seguir"
        self.accept()

    def _salir(self):
        self.accion = "salir"
        self.accept()


class ItemCestaWidget(QFrame):
    incrementar = pyqtSignal(str)
    decrementar = pyqtSignal(str)
    eliminar    = pyqtSignal(str)

    def __init__(self, nombre, precio, cantidad, parent=None):
        super().__init__(parent)
        self.nombre   = nombre
        self.precio   = precio
        self.cantidad = cantidad
        self._build()

    def _build(self):
        self.setStyleSheet(f"""
            QFrame{{background:{C_CARD};border-radius:16px;}}
            QLabel{{background:transparent;}}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(10)

        lbl_nombre = QLabel(self.nombre)
        lbl_nombre.setStyleSheet(f"color:{C_WHITE};font-size:13px;font-weight:700;")
        lbl_nombre.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        lbl_precio = QLabel(f"{self.precio:.2f} €/ud")
        lbl_precio.setStyleSheet(f"color:{C_MUTED};font-size:11px;")

        lbl_sub = QLabel(f"= {self.precio * self.cantidad:.2f} €")
        lbl_sub.setStyleSheet(f"color:{C_ORANGE};font-size:12px;font-weight:700;")

        info = QVBoxLayout()
        info.setSpacing(2)
        info.addWidget(lbl_nombre)
        info.addWidget(lbl_precio)
        info.addWidget(lbl_sub)

        lay.addLayout(info, 1)

        # Controles cantidad
        btn_menos = self._qty_btn("−", C_BG)
        lbl_cant  = QLabel(str(self.cantidad))
        lbl_cant.setAlignment(Qt.AlignCenter)
        lbl_cant.setStyleSheet(f"color:white;font-size:15px;font-weight:700;min-width:28px;")
        btn_mas   = self._qty_btn("+", C_ORANGE)

        btn_menos.clicked.connect(lambda: self.decrementar.emit(self.nombre))
        btn_mas.clicked.connect(lambda: self.incrementar.emit(self.nombre))

        ctrl = QHBoxLayout()
        ctrl.setSpacing(4)
        ctrl.addWidget(btn_menos)
        ctrl.addWidget(lbl_cant)
        ctrl.addWidget(btn_mas)
        lay.addLayout(ctrl)

        btn_del = QPushButton("🗑")
        btn_del.setFixedSize(36, 36)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet(f"QPushButton{{background:{C_RED};color:white;border:none;border-radius:18px;font-size:14px;}}QPushButton:hover{{background:#c62828;}}")
        btn_del.clicked.connect(lambda: self.eliminar.emit(self.nombre))
        lay.addWidget(btn_del)

    def _qty_btn(self, text, color):
        b = QPushButton(text)
        b.setFixedSize(32, 32)
        b.setCursor(Qt.PointingHandCursor)
        b.setStyleSheet(f"QPushButton{{background:{color};color:white;border:none;border-radius:16px;font-size:17px;font-weight:700;}}QPushButton:hover{{opacity:0.8;}}")
        return b


class CestaUI(QWidget):
    """
    Vista de la cesta. Recibe un ServicioCesta ya inicializado.
    Señales de navegación: volver_carta, ir_historial.
    """
    volver_carta  = pyqtSignal()
    cerrar_sesion = pyqtSignal()


    def __init__(self, servicio, parent=None):
        super().__init__(parent)
        self._srv = servicio
        self._build()
        self.refrescar()

    def _build(self):
        self.setStyleSheet(f"background:{C_BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet(f"background:{C_DARK};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(20, 12, 20, 12)

        btn_back = QPushButton("← Carta")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet(f"QPushButton{{background:transparent;color:{C_CREAM};border:none;font-size:13px;font-weight:700;}}QPushButton:hover{{color:{C_ORANGE};}}")
        btn_back.clicked.connect(self.volver_carta)
        h_lay.addWidget(btn_back)

        lbl_title = QLabel("🛒  Tu cesta")
        lbl_title.setStyleSheet(f"color:white;font-size:18px;font-weight:700;")
        lbl_title.setAlignment(Qt.AlignCenter)
        h_lay.addWidget(lbl_title, 1)

        self._lbl_puntos_header = QLabel("")
        self._lbl_puntos_header.setStyleSheet(f"background:{C_ORANGE};color:white;font-size:12px;font-weight:700;border-radius:14px;padding:6px 14px;")
        h_lay.addWidget(self._lbl_puntos_header)

        root.addWidget(header)

        # Línea naranja
        sep = QFrame()
        sep.setFixedHeight(3)
        sep.setStyleSheet(f"background:{C_ORANGE};")
        root.addWidget(sep)

        # ── Cuerpo: lista + panel lateral ────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Scroll de items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        self._items_container = QWidget()
        self._items_container.setStyleSheet("background:transparent;")
        self._items_layout = QVBoxLayout(self._items_container)
        self._items_layout.setContentsMargins(20, 16, 20, 16)
        self._items_layout.setSpacing(10)
        self._items_layout.addStretch()
        scroll.setWidget(self._items_container)
        body.addWidget(scroll, 1)

        # Panel lateral derecho
        panel = QFrame()
        panel.setFixedWidth(260)
        panel.setStyleSheet(f"background:{C_DARK};border-left:2px solid {C_CARD};")
        p_lay = QVBoxLayout(panel)
        p_lay.setContentsMargins(18, 20, 18, 20)
        p_lay.setSpacing(14)

        # Total
        lbl_t = QLabel("TOTAL A PAGAR")
        lbl_t.setStyleSheet(f"color:{C_MUTED};font-size:10px;font-weight:700;")
        total_box = QFrame()
        total_box.setStyleSheet(f"background:{C_BG};border-radius:12px;")
        tb_lay = QVBoxLayout(total_box)
        tb_lay.setContentsMargins(12, 12, 12, 12)
        lbl_apagar = QLabel("A pagar")
        lbl_apagar.setStyleSheet(f"color:{C_MUTED};font-size:11px;")
        lbl_apagar.setAlignment(Qt.AlignCenter)
        self._lbl_total = QLabel("0,00 €")
        self._lbl_total.setStyleSheet(f"color:white;font-size:26px;font-weight:800;")
        self._lbl_total.setAlignment(Qt.AlignCenter)
        tb_lay.addWidget(lbl_apagar)
        tb_lay.addWidget(self._lbl_total)

        # Puntos
        lbl_pts = QLabel("TUS PUNTOS")
        lbl_pts.setStyleSheet(f"color:{C_MUTED};font-size:10px;font-weight:700;")
        puntos_box = QFrame()
        puntos_box.setStyleSheet(f"background:{C_CARD};border-radius:12px;")
        pb_lay = QVBoxLayout(puntos_box)
        pb_lay.setContentsMargins(12, 10, 12, 10)
        self._lbl_puntos = QLabel("0")
        self._lbl_puntos.setStyleSheet(f"color:{C_ORANGE};font-size:24px;font-weight:800;")
        self._lbl_puntos.setAlignment(Qt.AlignCenter)
        lbl_pts_sub = QLabel("puntos disponibles")
        lbl_pts_sub.setStyleSheet(f"color:{C_MUTED};font-size:11px;")
        lbl_pts_sub.setAlignment(Qt.AlignCenter)
        pb_lay.addWidget(self._lbl_puntos)
        pb_lay.addWidget(lbl_pts_sub)

        # Descuento
        self._lbl_descuento = QLabel("")
        self._lbl_descuento.setStyleSheet(f"color:#81C784;font-size:12px;font-weight:700;")
        self._lbl_descuento.setAlignment(Qt.AlignCenter)
        self._lbl_descuento.hide()

        # Botones acción
        self._btn_canjear   = _btn("Canjear puntos",   C_ORANGE)
        btn_finalizar        = _btn("Finalizar pedido",  C_GREEN)
        btn_abandonar        = _btn("Abandonar pedido",  C_RED)

        self._btn_canjear.clicked.connect(self._accion_canjear)
        btn_finalizar.clicked.connect(self._accion_finalizar)
        btn_abandonar.clicked.connect(self._accion_abandonar)

        p_lay.addWidget(lbl_t)
        p_lay.addWidget(total_box)
        p_lay.addWidget(lbl_pts)
        p_lay.addWidget(puntos_box)
        p_lay.addWidget(self._lbl_descuento)
        p_lay.addStretch()
        p_lay.addWidget(self._btn_canjear)
        p_lay.addWidget(btn_finalizar)
        p_lay.addWidget(btn_abandonar)

        body.addWidget(panel)
        root.addLayout(body, 1)

    # ── Refresco ─────────────────────────────────────────────────────────────

    def refrescar(self):
        # Limpiar lista
        while self._items_layout.count() > 1:
            item = self._items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self._srv.obtener_items()

        if not items:
            lbl = QLabel("🛒  Tu cesta está vacía")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color:{C_MUTED};font-size:16px;font-weight:600;")
            self._items_layout.insertWidget(0, lbl)
        else:
            for it in items:
                w = ItemCestaWidget(it["nombre"], it["precio"], it["cantidad"])
                w.incrementar.connect(self._incrementar)
                w.decrementar.connect(self._decrementar)
                w.eliminar.connect(self._confirmar_eliminar)
                self._items_layout.insertWidget(self._items_layout.count() - 1, w)

        total   = self._srv.calcular_total()
        puntos  = self._srv.puntos_disponibles
        desc    = self._srv.descuento_aplicado

        self._lbl_total.setText(f"{total:.2f} €".replace(".", ","))
        self._lbl_puntos.setText(str(puntos))
        if self._srv.permite_puntos:
            self._lbl_puntos_header.setText(f"{puntos} pts")
        else:
            self._lbl_puntos_header.setText("Cajero")

        if self._srv.permite_puntos and desc > 0:
            self._lbl_descuento.setText(f"Descuento: -{desc:.2f} €")
            self._lbl_descuento.show()
        else:
            self._lbl_descuento.hide()

        if not self._srv.permite_puntos:
            self._btn_canjear.setText("Puntos desactivados")
            self._btn_canjear.setEnabled(False)
            self._btn_canjear.setStyleSheet(self._btn_canjear.styleSheet().replace(C_ORANGE, "#607D8B"))
        elif self._srv.puntos_canjeados:
            self._btn_canjear.setText("Puntos canjeados")
            self._btn_canjear.setEnabled(False)
            self._btn_canjear.setStyleSheet(self._btn_canjear.styleSheet().replace(C_ORANGE, "#607D8B"))

    # ── Acciones ─────────────────────────────────────────────────────────────

    def _incrementar(self, nombre):
        self._srv.incrementar(nombre)
        self.refrescar()

    def _decrementar(self, nombre):
        self._srv.decrementar(nombre)
        self.refrescar()

    def _confirmar_eliminar(self, nombre):
        dlg = ConfirmDialog("¿Eliminar producto?",
                            f"Se eliminará «{nombre}» de tu cesta.",
                            self, C_RED)
        dlg.exec_()
        if dlg.resultado:
            self._srv.eliminar_item(nombre)
            self.refrescar()

    def _accion_canjear(self):
        if not self._srv.permite_puntos:
            return
        if self._srv.puntos_canjeados:
            return
        if self._srv.puntos_disponibles == 0:
            QMessageBox.information(self, "Sin puntos", "No tienes puntos disponibles.")
            return
        if not self._srv.obtener_items():
            QMessageBox.information(self, "Cesta vacía", "Añade productos primero.")
            return
        desc = min(self._srv.puntos_disponibles / 100, self._srv.calcular_subtotal())
        dlg = ConfirmDialog("¿Canjear puntos?",
                            f"Usarás {self._srv.puntos_disponibles} puntos → descuento de {desc:.2f} €.",
                            self, C_ORANGE)
        dlg.exec_()
        if dlg.resultado:
            self._srv.canjear_puntos()
            self.refrescar()

    def _accion_finalizar(self):
        if not self._srv.obtener_items():
            QMessageBox.information(self, "Cesta vacía", "Añade productos antes de finalizar.")
            return
        total = self._srv.calcular_total()
        dlg = ConfirmDialog("¿Finalizar pedido?",
                            f"Total a pagar: {total:.2f} €\nSe generará un ID único para presentar en caja.",
                            self, C_GREEN)
        dlg.exec_()
        if dlg.resultado:
            try:
                codigo, pts_ganados = self._srv.finalizar_pedido()
                resultado_dlg = PedidoConfirmadoDialog(codigo, pts_ganados, self)
                resultado_dlg.exec_()
                if resultado_dlg.accion == "seguir":
                    self.volver_carta.emit()
                elif resultado_dlg.accion == "salir":
                    self.cerrar_sesion.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _accion_abandonar(self):
        if not self._srv.obtener_items():
            QMessageBox.information(self, "Cesta vacía", "No hay productos en la cesta.")
            return
        dlg = ConfirmDialog("¿Abandonar pedido?",
                            "Se vaciará tu cesta y perderás todos los productos.",
                            self, C_RED)
        dlg.exec_()
        if dlg.resultado:
            self._srv.vaciar_cesta()
            self.refrescar()
