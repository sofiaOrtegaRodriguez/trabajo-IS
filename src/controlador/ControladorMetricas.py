class ControladorMetricas:
    def __init__(self, ref_modelo):
        self._modelo = ref_modelo

    def obtener_metricas(self, fecha_inicio=None, fecha_fin=None):
        return self._modelo.obtenerMetricasGerente(fecha_inicio, fecha_fin)
