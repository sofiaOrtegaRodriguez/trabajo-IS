from src.modelo.dao.MetricasDaoJDBC import MetricasDaoJDBC


class ServicioMetricas:
    def obtenerMetricasGerente(self, fecha_inicio=None, fecha_fin=None):
        return MetricasDaoJDBC().obtener_metricas(fecha_inicio, fecha_fin)

    def prepararDashboardGerenteVista(self, fecha_inicio=None, fecha_fin=None, seleccion_categoria="Todas las categorias", order_desc=True):
        data = self.obtenerMetricasGerente(fecha_inicio, fecha_fin)
        resumen = data["resumen"]
        empleados = list(data["empleados"] or [])
        categorias = list(data["categorias"] or [])
        mensuales = list(data["mensuales"] or [])
        diarios = list(data["diarios"] or [])
        inicio = data.get("inicio", fecha_inicio)
        fin = data.get("fin", fecha_fin)
        total_empleados = sum(int(item.get("total", 0) or 0) for item in empleados)
        empleados_texto = "\n".join(f'{item["tipo"]}: {item["total"]}' for item in empleados) if empleados else "Todavia no hay empleados cargados."
        days_selected = (fin - inicio).days if inicio is not None and fin is not None else 0
        grafico_series = diarios if days_selected <= 31 else mensuales
        grafico_titulo = "Ganancias diarias" if days_selected <= 31 else "Ganancias por mes"
        categorias_opciones = ["Todas las categorias"]
        for item in categorias:
            categoria = str(item.get("categoria", "")).strip()
            if categoria and categoria not in categorias_opciones:
                categorias_opciones.append(categoria)
        categorias_plan = self.prepararCategoriasMetricas(categorias, seleccion_categoria, order_desc)
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

    def prepararCategoriasMetricas(self, categorias, seleccion="Todas las categorias", order_desc=True):
        categorias = list(categorias or [])
        seleccion = str(seleccion).strip()
        if not categorias or not seleccion:
            return {"tipo": "vacio", "mensaje": "No hay ventas en las categorias seleccionadas.", "summary": ""}
        if seleccion == "Todas las categorias":
            bloques = []
            for category in categorias:
                items = list(category.get("items", []))
                if not items:
                    continue
                items.sort(key=lambda item: (item["total"], item["nombre"]), reverse=order_desc)
                bloques.append({"titulo": category["categoria"], "items": items, "total_categoria": sum(item["total"] for item in items)})
            bloques.sort(key=lambda block: (block["total_categoria"], block["titulo"]), reverse=order_desc)
            if not bloques:
                return {"tipo": "vacio", "mensaje": "No hay ventas en las categorias seleccionadas.", "summary": ""}
            return {"tipo": "bloques", "bloques": bloques, "summary": "Mostrando todas las categorias."}
        category = next((item for item in categorias if item["categoria"] == seleccion), None)
        if category is None:
            return {"tipo": "vacio", "mensaje": "No hay ventas en la categoria seleccionada.", "summary": ""}
        items = list(category.get("items", []))
        items.sort(key=lambda item: (item["total"], item["nombre"]), reverse=order_desc)
        return {"tipo": "bloques", "bloques": [{"titulo": category["categoria"], "items": items, "total_categoria": sum(item["total"] for item in items)}], "summary": f"Mostrando {'mas vendidos' if order_desc else 'menos vendidos'} de {category['categoria']}."}
