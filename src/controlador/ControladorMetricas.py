class ControladorMetricas:
    def __init__(self, ref_modelo):
        self._modelo = ref_modelo

    def obtener_metricas(self, fecha_inicio=None, fecha_fin=None):
        return self._modelo.obtenerMetricasGerente(fecha_inicio, fecha_fin)

    def preparar_categorias_metricas(self, categorias, seleccion="Todas las categorias", order_desc=True):
        return self._modelo.prepararCategoriasMetricas(categorias, seleccion, order_desc)

    def preparar_dashboard_gerente(self, fecha_inicio=None, fecha_fin=None, seleccion_categoria="Todas las categorias", order_desc=True):
        return self._modelo.prepararDashboardGerenteVista(fecha_inicio, fecha_fin, seleccion_categoria, order_desc)
