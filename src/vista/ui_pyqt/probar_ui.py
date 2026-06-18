from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
import sys
import os

app = QApplication(sys.argv)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(BASE_DIR, "pedidosUI.ui")

print("Cargando:", ui_path)  # debug útil

window = uic.loadUi(ui_path)
window.show()

sys.exit(app.exec_())