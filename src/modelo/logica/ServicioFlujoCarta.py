import os as _os


class ServicioFlujoCarta:
    # Ruta absoluta a src/vista/imagenes/comida, calculada una vez en tiempo de clase.
    _IMAGE_ROOT = _os.path.normpath(
        _os.path.join(_os.path.dirname(__file__), "..", "..", "vista", "imagenes", "comida")
    )

    def __init__(self, modelo, cesta):
        self._modelo = modelo
        self._cesta = cesta
        self.categoria_actual = "sushi"
        self.pagina_actual = 1

    def cargar_pagina_actual(self):
        return self._modelo.obtenerProductosCategoriaRender(
            self.categoria_actual,
            self.pagina_actual,
            4,
            cesta=self._cesta.cantidad_producto,
            image_root=self._IMAGE_ROOT,
        )

    def cambiar_categoria(self, categoria):
        self.categoria_actual = categoria
        self.pagina_actual = 1
        return self.cargar_pagina_actual()

    def mover_pagina(self, delta):
        nueva_pagina = self.pagina_actual + int(delta)
        resultado = self._modelo.obtenerProductosCategoriaPaginados(self.categoria_actual, nueva_pagina, 4)
        self.pagina_actual = resultado["pagina_actual"]
        return self.cargar_pagina_actual()
