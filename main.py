import os
import sys

from PyQt5.QtWidgets import QApplication

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.controlador.ControladorPrincipal import ControladorPrincipal
from src.controlador.ControladorAdmin import ControladorAdmin
from src.controlador.ControladorCliente import ControladorCliente
from src.controlador.ControladorCesta import ControladorCesta
from src.controlador.ControladorProductos import ControladorProductos
from src.controlador.ControladorEmpleados import ControladorEmpleados
from src.controlador.ControladorPedidos import ControladorPedidos
from src.controlador.ControladorMetricas import ControladorMetricas
from src.modelo.Logica import Logica
from src.vista.VentanaPrincipal import VentanaPrincipal


def main():
    app = QApplication(sys.argv)

    # ── Modelo ────────────────────────────────────────────────────────────────
    modelo = Logica()

    # ── Controladores específicos (sin rol, sin vista) ────────────────────────
    controlador_cesta     = ControladorCesta(modelo.crear_servicio_cesta())
    controlador_productos = ControladorProductos(modelo)
    controlador_empleados = ControladorEmpleados(modelo)
    controlador_pedidos   = ControladorPedidos(modelo)
    controlador_metricas  = ControladorMetricas(modelo)

    # ── Vista ──────────────────────────────────────────────────────────────────
    ventana = VentanaPrincipal()

    # ── Controladores de rol (necesitan referencia a la vista) ────────────────
    controlador_principal = ControladorPrincipal(ventana, modelo, controlador_cesta)
    controlador_admin     = ControladorAdmin(
        modelo, ventana, controlador_productos, controlador_empleados
    )
    controlador_cliente   = ControladorCliente(
        modelo, ventana, controlador_cesta, controlador_productos
    )

    # ── Inyección cruzada: ControladorPrincipal conoce los controladores de rol
    controlador_principal.set_controladores_rol(
        controlador_admin, controlador_cliente, controlador_pedidos, controlador_metricas
    )

    # ── Inyección en la vista ─────────────────────────────────────────────────
    ventana.set_controlador(
        controlador_principal,
        ctrl_admin=controlador_admin,
        ctrl_cliente=controlador_cliente,
        ctrl_pedidos=controlador_pedidos,
        ctrl_metricas=controlador_metricas,
    )

    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
