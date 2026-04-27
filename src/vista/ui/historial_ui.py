"""
Vista del Historial de Pedidos — PyQt5.
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy,
)

C_BG      = "#147DB2"
C_DARK    = "#072D44"
C_CARD    = "#5CA9D0"
C_CARD_INNER = "#4A95BA"
C_ORANGE  = "#FC814A"
C_ORANGE_D= "#E66E3A"
C_CREAM   = "#FEF5ED"
C_WHITE   = "#FFFFFF"
C_MUTED   = "#B6D5E2"
C_RED_BG  = "#4A2020"
C_RED_ACC = "#C06060"


class PedidoCard(QFrame):
    def __init__(self, pedido, parent=None):
        super().__init__(parent)
        cancelado = pedido.estado == "cancelado"
        bg     = C_RED_BG  if cancelado else C_CARD
        accent = C_RED_ACC if cancelado else C_ORANGE
        self.setStyleSheet(f"QFrame{{background:{bg};border-radius:18px;}}QLabel{{background:transparent;}}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 16)
        lay.setSpacing(0)

        # Barra superior
        bar = QFrame()
        bar.setFixedHeight(5)
        bar.setStyleSheet(f"background:{accent};border-radius:3px;")
        lay.addWidget(bar)

        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        i_lay = QVBoxLayout(inner)
        i_lay.setContentsMargins(18, 12, 18, 0)
        i_lay.setSpacing(8)

        # Cabecera
        h_row = QHBoxLayout()
        lbl_id = QLabel(f"Pedido #{pedido.id:04d}")
        lbl_id.setStyleSheet(f"color:{C_WHITE};font-size:14px;font-weight:700;")
        estado_txt = "✗  Cancelado" if cancelado else "✓  Completado"
        estado_bg  = C_RED_ACC if cancelado else C_BG
        lbl_estado = QLabel(estado_txt)
        lbl_estado.setStyleSheet(f"background:{estado_bg};color:{C_WHITE};font-size:11px;font-weight:700;border-radius:10px;padding:4px 12px;")
        h_row.addWidget(lbl_id)
        h_row.addStretch()
        h_row.addWidget(lbl_estado)
        i_lay.addLayout(h_row)

        # Fecha/hora
        lbl_fecha = QLabel(f"📅  {pedido.fecha}     🕐  {pedido.hora}")
        lbl_fecha.setStyleSheet(f"color:{C_MUTED};font-size:11px;font-family:Courier;")
        i_lay.addWidget(lbl_fecha)

        # Separador
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{C_CARD_INNER};")
        i_lay.addWidget(sep)

        # Productos
        lbl_prods = QLabel("PRODUCTOS")
        lbl_prods.setStyleSheet(f"color:{C_MUTED};font-size:9px;font-weight:700;")
        i_lay.addWidget(lbl_prods)

        prod_box = QFrame()
        prod_box.setStyleSheet(f"background:{C_CARD_INNER};border-radius:10px;")
        pb_lay = QVBoxLayout(prod_box)
        pb_lay.setContentsMargins(12, 8, 12, 8)
        pb_lay.setSpacing(4)
        for prod in pedido.productos:
            row = QHBoxLayout()
            lbl_n = QLabel(f"·  {prod.nombre_producto}")
            lbl_n.setStyleSheet(f"color:{C_WHITE};font-size:12px;")
            lbl_c = QLabel(f"×{prod.cantidad}")
            lbl_c.setStyleSheet(f"color:{C_MUTED};font-size:11px;")
            lbl_s = QLabel(f"{prod.subtotal:.2f} €")
            lbl_s.setStyleSheet(f"color:{C_ORANGE};font-size:12px;font-weight:700;")
            row.addWidget(lbl_n, 1)
            row.addWidget(lbl_c)
            row.addWidget(lbl_s)
            pb_lay.addLayout(row)
        i_lay.addWidget(prod_box)

        # Total
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background:{C_CARD_INNER};")
        i_lay.addWidget(sep2)

        total_row = QHBoxLayout()
        lbl_tl = QLabel("TOTAL PAGADO")
        lbl_tl.setStyleSheet(f"color:{C_MUTED};font-size:10px;font-weight:700;")
        lbl_tv = QLabel(f"{pedido.total:.2f} €")
        lbl_tv.setStyleSheet(f"color:{C_ORANGE};font-size:18px;font-weight:800;")
        total_row.addWidget(lbl_tl)
        total_row.addStretch()
        total_row.addWidget(lbl_tv)
        i_lay.addLayout(total_row)

        lay.addWidget(inner)


class HistorialUI(QWidget):
    volver_menu  = pyqtSignal()
    cerrar_sesion = pyqtSignal()

    def __init__(self, cliente, pedidos, parent=None):
        super().__init__(parent)
        self._cliente = cliente
        self._pedidos = pedidos
        self._build()

    def _build(self):
        self.setStyleSheet(f"background:{C_BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ──────────────────────────────────────────
        topbar = QFrame()
        topbar.setStyleSheet(f"background:{C_DARK};")
        tb_lay = QHBoxLayout(topbar)
        tb_lay.setContentsMargins(16, 10, 16, 10)

        btn_back = QPushButton("← Inicio")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet(f"QPushButton{{background:transparent;color:{C_CREAM};border:none;font-size:13px;font-weight:700;}}QPushButton:hover{{color:{C_ORANGE};}}")
        btn_back.clicked.connect(self.volver_menu)
        tb_lay.addWidget(btn_back)

        lbl_title = QLabel("HISTORIAL DE PEDIDOS")
        lbl_title.setStyleSheet(f"color:{C_WHITE};font-size:14px;font-weight:700;")
        lbl_title.setAlignment(Qt.AlignCenter)
        tb_lay.addWidget(lbl_title, 1)

        pts_box = QFrame()
        pts_box.setStyleSheet(f"background:{C_CREAM};border-radius:14px;border:2px solid {C_ORANGE};")
        pts_lay = QHBoxLayout(pts_box)
        pts_lay.setContentsMargins(12, 6, 12, 6)
        pts_lay.setSpacing(4)
        QLabel("⭐", pts_box).setParent(None)
        lbl_star = QLabel("⭐")
        lbl_star.setStyleSheet("background:transparent;color:#FC814A;font-size:13px;")
        lbl_pv = QLabel(str(self._cliente.puntos))
        lbl_pv.setStyleSheet(f"background:transparent;color:{C_DARK};font-size:14px;font-weight:700;")
        lbl_psub = QLabel(" pts")
        lbl_psub.setStyleSheet(f"background:transparent;color:#607D8B;font-size:11px;")
        pts_lay.addWidget(lbl_star)
        pts_lay.addWidget(lbl_pv)
        pts_lay.addWidget(lbl_psub)
        tb_lay.addWidget(pts_box)

        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet(f"QPushButton{{background:{C_ORANGE};color:white;border:none;border-radius:16px;font-size:12px;font-weight:700;padding:6px 14px;}}QPushButton:hover{{background:{C_ORANGE_D};}}")
        btn_logout.clicked.connect(self._confirmar_cierre)
        tb_lay.addWidget(btn_logout)
        root.addWidget(topbar)

        sep = QFrame()
        sep.setFixedHeight(3)
        sep.setStyleSheet(f"background:{C_ORANGE};")
        root.addWidget(sep)

        # ── Subheader ────────────────────────────────────────
        sub = QFrame()
        sub.setStyleSheet(f"background:{C_DARK};")
        s_lay = QHBoxLayout(sub)
        s_lay.setContentsMargins(20, 10, 20, 10)
        lbl_bienvenida = QLabel(f"Bienvenid@, {self._cliente.nombre}")
        lbl_bienvenida.setStyleSheet(f"color:{C_WHITE};font-size:13px;font-weight:700;")
        n = len(self._pedidos)
        lbl_n = QLabel(f"{n} pedido{'s' if n != 1 else ''} registrado{'s' if n != 1 else ''}")
        lbl_n.setStyleSheet(f"color:{C_MUTED};font-size:11px;")
        s_lay.addWidget(lbl_bienvenida)
        s_lay.addStretch()
        s_lay.addWidget(lbl_n)
        root.addWidget(sub)

        # ── Scroll de pedidos ─────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        container = QWidget()
        container.setStyleSheet("background:transparent;")
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(20, 16, 20, 16)
        c_lay.setSpacing(14)

        if not self._pedidos:
            lbl_empty = QLabel("Aún no tienes pedidos registrados.")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet(f"color:{C_MUTED};font-size:15px;font-weight:600;")
            c_lay.addWidget(lbl_empty)
        else:
            for pedido in self._pedidos:
                c_lay.addWidget(PedidoCard(pedido))

        c_lay.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

    def _confirmar_cierre(self):
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Cerrar sesión")
        msg.setText("¿Seguro que quieres cerrar sesión?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("Sí, salir")
        msg.button(QMessageBox.No).setText("Cancelar")
        msg.setStyleSheet("background-color: #072D44; color: white; font-size: 14px;")
        if msg.exec_() == QMessageBox.Yes:
            self.cerrar_sesion.emit()