import os
import sys

from PyQt5.QtWidgets import QApplication


ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.controlador.ControladorPrincipalNuevo import ControladorPrincipal
from src.modelo.Logica import Logica
from src.vista.VentanaPrincipal import VentanaPrincipal


def main():
    app = QApplication(sys.argv)

    modelo = Logica()
    ventana = VentanaPrincipal()
    controlador = ControladorPrincipal(ventana, modelo)

    ventana.set_controlador(controlador)
    ventana.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
