from PyQt5.QtWidgets import QApplication

from src.vista.LoginNueva import MiVentana
from src.modelo.Logica import Logica
from src.controlador.ControladorPrincipalNuevo import ControladorPrincipal

if __name__ == "__main__":
    app = QApplication([])
    ventana = MiVentana()
    modelo = Logica()
    controlador = ControladorPrincipal(ventana, modelo)

    ventana.controlador = controlador
    controlador.ventanaIniciarSesión()

    app.exec_()

