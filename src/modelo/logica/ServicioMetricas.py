from src.modelo.dao.MetricasDaoJDBC import MetricasDaoJDBC


class ServicioMetricas:
    """
    Servicio de lógica de negocio para las métricas del dashboard del gerente.

    Responsabilidades:
      - Obtener los datos crudos de la BD a través de MetricasDaoJDBC
      - Transformar y organizar esos datos en la estructura exacta que
        espera la vista (GerenteDashboardUI) para renderizar sin lógica propia
      - Decidir qué gráfico mostrar (diario vs mensual) según el rango de fechas
      - Ordenar y filtrar el ranking de categorías según la selección del usuario

    No contiene acceso directo a la BD: siempre delega en el DAO.
    """

    # ─────────────────────────────────────────────────────────────
    # MÉTODO PÚBLICO: obtención de datos crudos
    # ─────────────────────────────────────────────────────────────

    def obtenerMetricasGerente(self, fecha_inicio=None, fecha_fin=None):
        """
        Devuelve los datos crudos del DAO sin transformación.
        Si no se pasan fechas, el DAO usará un rango por defecto.

        La estructura devuelta por el DAO incluye:
          - "resumen":   dict con pedidos, clientes, ingresos totales
          - "empleados": lista de dicts con tipo y total por tipo
          - "categorias":lista de dicts con categoría e items vendidos
          - "mensuales": serie temporal de ingresos agrupados por mes
          - "diarios":   serie temporal de ingresos agrupados por día
          - "inicio" / "fin": fechas reales usadas por la consulta
        """
        return MetricasDaoJDBC().obtener_metricas(fecha_inicio, fecha_fin)

    # ─────────────────────────────────────────────────────────────
    # MÉTODO PÚBLICO: preparación completa del dashboard
    # ─────────────────────────────────────────────────────────────

    def prepararDashboardGerenteVista(self, fecha_inicio=None, fecha_fin=None, seleccion_categoria="Todas las categorias", order_desc=True):
        """
        Transforma todos los datos crudos del DAO en la estructura lista
        para que el controlador la pase directamente a la vista.

        Parámetros:
          fecha_inicio, fecha_fin: rango de fechas del filtro (pueden ser None)
          seleccion_categoria:     categoría seleccionada en el combobox de la vista
          order_desc:              True = más vendidos primero, False = menos vendidos primero

        Devuelve un dict con cuatro secciones:
          {
            "resumen":        dict con pedidos, clientes, ingresos  → tarjetas de métricas
            "total_empleados": int                                  → tarjeta de empleados
            "empleados_texto": str multilínea                       → caja de texto empleados
            "grafico": {
              "series":  lista de dicts con label e ingresos        → RevenueCanvas
              "titulo":  str                                        → título del gráfico
            },
            "categorias": {
              "opciones":  lista de str                             → combobox de categorías
              "plan":      dict con bloques del ranking             → panel de categorías
              "seleccion": str                                      → categoría activa
            },
          }
        """
        # ── 1. Obtiene los datos crudos del DAO ──────────────────
        data = self.obtenerMetricasGerente(fecha_inicio, fecha_fin)

        # Extrae cada sección del dict devuelto por el DAO
        resumen = data["resumen"]
        empleados = list(data["empleados"] or [])
        categorias = list(data["categorias"] or [])
        mensuales = list(data["mensuales"] or [])
        diarios = list(data["diarios"] or [])
        # El DAO puede devolver las fechas reales usadas (si corrigió el rango)
        inicio = data.get("inicio", fecha_inicio)
        fin = data.get("fin", fecha_fin)

        # ── 2. Calcula el total y el texto de empleados ──────────
        # Suma el total de todos los tipos de empleado
        total_empleados = sum(int(item.get("total", 0) or 0) for item in empleados)

        # Texto multilínea "tipo: total" por cada tipo de empleado
        # Si no hay empleados, muestra un mensaje informativo
        empleados_texto = (
            "\n".join(f'{item["tipo"]}: {item["total"]}' for item in empleados)
            if empleados
            else "Todavia no hay empleados cargados."
        )

        # ── 3. Decide qué serie temporal usar para el gráfico ────
        # Si el rango es de 31 días o menos → gráfico diario (más detalle)
        # Si el rango es mayor            → gráfico mensual (más compacto)
        days_selected = (fin - inicio).days if inicio is not None and fin is not None else 0
        grafico_series = diarios if days_selected <= 31 else mensuales
        grafico_titulo = "Ganancias diarias" if days_selected <= 31 else "Ganancias por mes"

        # ── 4. Construye la lista de opciones del combobox ───────
        # Siempre empieza con "Todas las categorias" y añade las que vengan de la BD
        categorias_opciones = ["Todas las categorias"]
        for item in categorias:
            categoria = str(item.get("categoria", "")).strip()
            if categoria and categoria not in categorias_opciones:  # evita duplicados
                categorias_opciones.append(categoria)

        # ── 5. Prepara el plan de bloques del ranking ────────────
        categorias_plan = self.prepararCategoriasMetricas(categorias, seleccion_categoria, order_desc)

        # ── 6. Devuelve el dict completo listo para la vista ─────
        return {
            "resumen": resumen,
            "total_empleados": total_empleados,
            "empleados_texto": empleados_texto,
            "grafico": {
                "series": grafico_series,
                "titulo": grafico_titulo,
            },
            "categorias": {
                "opciones": categorias_opciones,
                "plan": categorias_plan,
                "seleccion": seleccion_categoria,
            },
        }

    # ─────────────────────────────────────────────────────────────
    # MÉTODO PÚBLICO: preparación del ranking de categorías
    # ─────────────────────────────────────────────────────────────

    def prepararCategoriasMetricas(self, categorias, seleccion="Todas las categorias", order_desc=True):
        """
        Transforma la lista de categorías con sus productos vendidos en
        un "plan" que la vista usa para construir los bloques del ranking.

        Parámetros:
          categorias:  lista de dicts con "categoria" e "items" (productos vendidos)
          seleccion:   "Todas las categorias" o el nombre de una categoría concreta
          order_desc:  True = más vendidos primero, False = menos vendidos primero

        El "plan" devuelto es siempre un dict con:
          - "tipo": "bloques" | "vacio"
          - "bloques": lista de bloques (solo si tipo == "bloques")
          - "summary": texto resumen para mostrar encima del panel
          - "mensaje": texto de vacío (solo si tipo == "vacio")

        Cada bloque tiene:
          { "titulo": str, "items": lista ordenada, "total_categoria": int }

        Hay dos modos de funcionamiento:
          A) seleccion == "Todas las categorias" → un bloque por cada categoría,
             ordenados entre sí por total de ventas de la categoría
          B) seleccion == nombre concreto → un único bloque con esa categoría
        """
        categorias = list(categorias or [])
        seleccion = str(seleccion).strip()

        # Caso vacío: sin datos o sin selección
        if not categorias or not seleccion:
            return {"tipo": "vacio", "mensaje": "No hay ventas en las categorias seleccionadas.", "summary": ""}

        # ── Modo A: todas las categorías ─────────────────────────
        if seleccion == "Todas las categorias":
            bloques = []
            for category in categorias:
                items = list(category.get("items", []))
                if not items:
                    continue  # omite categorías sin ventas

                # Ordena los productos de la categoría por total vendido (y nombre como desempate)
                items.sort(key=lambda item: (item["total"], item["nombre"]), reverse=order_desc)

                bloques.append({
                    "titulo": category["categoria"],
                    "items": items,
                    "total_categoria": sum(item["total"] for item in items),  # para ordenar bloques entre sí
                })

            # Ordena los bloques entre sí por el total de ventas de cada categoría
            bloques.sort(key=lambda block: (block["total_categoria"], block["titulo"]), reverse=order_desc)

            if not bloques:
                return {"tipo": "vacio", "mensaje": "No hay ventas en las categorias seleccionadas.", "summary": ""}

            return {"tipo": "bloques", "bloques": bloques, "summary": "Mostrando todas las categorias."}

        # ── Modo B: una sola categoría ────────────────────────────
        # Busca la categoría seleccionada en la lista con next(); devuelve None si no existe
        category = next((item for item in categorias if item["categoria"] == seleccion), None)

        if category is None:
            return {"tipo": "vacio", "mensaje": "No hay ventas en la categoria seleccionada.", "summary": ""}

        items = list(category.get("items", []))
        # Ordena los productos de la categoría igual que en el modo A
        items.sort(key=lambda item: (item["total"], item["nombre"]), reverse=order_desc)

        return {
            "tipo": "bloques",
            "bloques": [{
                "titulo": category["categoria"],
                "items": items,
                "total_categoria": sum(item["total"] for item in items),
            }],
            # El summary describe qué se está viendo y en qué orden
            "summary": f"Mostrando {'mas vendidos' if order_desc else 'menos vendidos'} de {category['categoria']}.",
        }