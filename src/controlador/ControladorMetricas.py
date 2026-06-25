class ControladorMetricas:
    """
    Fachada entre la vista del gerente y el modelo para consultas de métricas.
    Solo delega; no contiene lógica propia.
    """

    def __init__(self, ref_modelo):
        self._modelo = ref_modelo

    def obtener_metricas(self, fecha_inicio=None, fecha_fin=None):
        """Devuelve las métricas brutas del gerente, opcionalmente filtradas por rango de fechas."""
        return self._modelo.obtenerMetricasGerente(fecha_inicio, fecha_fin)

    def preparar_categorias_metricas(self, categorias, seleccion="Todas las categorias", order_desc=True):
        """
        Filtra y ordena la lista de categorías para el selector de la vista.
          - seleccion: categoría activa en el filtro ('Todas las categorias' = sin filtro)
          - order_desc: True = mayor a menor
        """
        return self._modelo.prepararCategoriasMetricas(categorias, seleccion, order_desc)

    def preparar_dashboard_gerente(self, fecha_inicio=None, fecha_fin=None, seleccion_categoria="Todas las categorias", order_desc=True):
        """
        Devuelve todos los datos necesarios para renderizar el dashboard del gerente
        (métricas, categorías ordenadas, filtros aplicados) en una sola llamada.
        """
        return self._modelo.prepararDashboardGerenteVista(fecha_inicio, fecha_fin, seleccion_categoria, order_desc)