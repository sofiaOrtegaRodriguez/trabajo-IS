from datetime import datetime
from src.modelo.dao.PedidoDaoJDBC import PedidoDaoJDBC


class ServicioPedidos:
    def crearPedido(self, sesion, items, total):
        return PedidoDaoJDBC().crear(sesion, items, total)

    def listarPedidos(self, sesion):
        return PedidoDaoJDBC().listar(sesion)

    def listarTodosPedidos(self):
        return PedidoDaoJDBC().listarTiempoReal()

    def filtrarPedidosPorEstado(self, pedidos, estado="TODOS"):
        estado = str(estado).strip().upper()
        if estado == "TODOS":
            return list(pedidos)
        return [pedido for pedido in pedidos if str(getattr(pedido, "estado", "")).upper() == estado]

    def prepararPedidosVista(self, pedidos, estado="TODOS"):
        pedidos_filtrados = self.filtrarPedidosPorEstado(pedidos, estado)
        estado = str(estado).strip().upper()
        if not pedidos_filtrados:
            mensaje = f"No hay pedidos con el estado '{estado}' hoy." if estado != "TODOS" else "No hay pedidos registrados hoy."
            return {"tipo": "vacio", "mensaje": mensaje, "pedidos": [], "pedidos_vista": []}
        return {"tipo": "lista", "pedidos": list(pedidos_filtrados), "pedidos_vista": [self._construir_pedido_vista(pedido) for pedido in pedidos_filtrados]}

    def establecerFiltroPedidos(self, estado="TODOS"):
        self._filtro_pedidos = str(estado).strip().upper() or "TODOS"
        return self._filtro_pedidos

    def obtenerFiltroPedidos(self):
        return self._filtro_pedidos

    def obtenerEstadosPedidoPermitidos(self):
        return ["PENDIENTE", "PAGADO", "PREPARANDO", "LISTO"]

    def obtenerFiltrosPedidoDisponibles(self):
        return ["TODOS"] + self.obtenerEstadosPedidoPermitidos()

    def actualizarEstadoPedido(self, pedido):
        return PedidoDaoJDBC().modificarEstado(pedido)

    def _construir_pedido_vista(self, pedido):
        fecha_origen = getattr(pedido, "fecha", None)
        hora_texto = fecha_origen.strftime("%H:%M:%S") if isinstance(fecha_origen, datetime) else (str(fecha_origen).split(".")[0][-8:] if fecha_origen else "--:--:--")
        datos_productos = getattr(pedido, "productos", None)
        texto_productos = "\n".join([f"• {prod.cantidad}x {prod.nombre_producto}" for prod in datos_productos]) if isinstance(datos_productos, list) else (str(datos_productos) if datos_productos else "Sin productos registrados.")
        estado_actual = str(getattr(pedido, "estado", "")).strip().lower()
        return {"id": getattr(pedido, "id", None), "cliente": getattr(pedido, "usuario", None) or "Anónimo", "origen": "Kiosco", "hora_texto": hora_texto, "texto_productos": texto_productos, "total": float(getattr(pedido, "total", 0) or 0), "estado": estado_actual, "estado_display": estado_actual.upper(), "estilo": self._estilo_estado_pedido(estado_actual), "estados_permitidos": self._estados_con_actual(estado_actual)}

    def _estados_con_actual(self, estado_actual):
        estados = list(self.obtenerEstadosPedidoPermitidos() or [])
        estado_display = estado_actual.upper()
        if estado_display not in estados:
            estados = [estado_display] + estados
        return estados

    def _estilo_estado_pedido(self, estado):
        estilos = {"pagado": {"bg": "#1C3B2F", "accent": "#34D399", "text": "#34D399"}, "pendiente": {"bg": "#3A2A1A", "accent": "#FC814A", "text": "#FC814A"}, "preparando": {"bg": "#2E2440", "accent": "#A855F7", "text": "#A855F7"}, "listo": {"bg": "#1E293B", "accent": "#38BDF8", "text": "#38BDF8"}}
        return estilos.get(str(estado).strip().lower(), estilos["pendiente"])
