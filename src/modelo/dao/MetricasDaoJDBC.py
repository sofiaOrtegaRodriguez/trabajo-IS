from datetime import date, datetime

from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer
from src.modelo.dao.MetricasDao import MetricasDao


class MetricasDaoJDBC(MetricasDao, ConexionSQLServer):
    def obtener_metricas(self, fecha_inicio=None, fecha_fin=None):
        inicio, fin = self._normalizar_rango(fecha_inicio, fecha_fin)
        cursor = self.getCursor()
        try:
            category_column = self._get_category_column(cursor)
            resumen = self._fetch_resumen(cursor, inicio, fin)
            empleados = self._fetch_empleados(cursor)
            categorias = self._fetch_productos_por_categoria(cursor, inicio, fin, category_column)
            mensuales = self._fetch_ingresos_mensuales(cursor, inicio, fin)
            diarios = self._fetch_ingresos_diarios(cursor, inicio, fin)
            return {"resumen": resumen, "empleados": empleados, "categorias": categorias, "mensuales": mensuales, "diarios": diarios, "inicio": inicio, "fin": fin}
        except Exception as exc:
            raise RuntimeError(f"No se pudieron cargar las metricas del gerente: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    def _normalizar_rango(self, fecha_inicio, fecha_fin):
        if fecha_inicio is None:
            fecha_fin = date.today() if fecha_fin is None else self._coerce_date(fecha_fin)
            return fecha_fin.replace(day=1), fecha_fin
        inicio = self._coerce_date(fecha_inicio)
        fin = self._coerce_date(fecha_fin or fecha_inicio)
        return (fin, inicio) if fin < inicio else (inicio, fin)

    def _coerce_date(self, value):
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        raise TypeError("Fecha no valida")

    def _fetch_resumen(self, cursor, inicio, fin):
        cursor.execute(
            """
            SELECT COUNT(*) AS pedidos,
                   COUNT(DISTINCT CASE WHEN IDCli IS NOT NULL THEN IDCli END) AS clientes,
                   COALESCE(SUM(PrecioTotal), 0) AS ingresos,
                   COALESCE(SUM(CASE WHEN IDCli IS NOT NULL THEN PrecioTotal ELSE 0 END), 0) AS ingresos_clientes
            FROM PEDIDOS
            WHERE Hora >= ? AND Hora < DATEADD(day, 1, ?)
            """,
            (inicio, fin),
        )
        row = cursor.fetchone()
        return {"pedidos": int(getattr(row, "pedidos", 0) or 0), "clientes": int(getattr(row, "clientes", 0) or 0), "ingresos": round(float(getattr(row, "ingresos", 0) or 0), 2), "ingresos_clientes": round(float(getattr(row, "ingresos_clientes", 0) or 0), 2)}

    def _fetch_empleados(self, cursor):
        cursor.execute(
            """
            SELECT Emp_Tipo, COUNT(*) AS total
            FROM EMPLEADOS
            GROUP BY Emp_Tipo
            ORDER BY Emp_Tipo
            """
        )
        return [{"tipo": row.Emp_Tipo, "total": int(row.total or 0)} for row in cursor.fetchall()]

    def _fetch_productos_por_categoria(self, cursor, inicio, fin, category_column):
        if category_column is None:
            return [{"categoria": "Sin categoria", "items": []}]
        cursor.execute(
            f"""
            SELECT LTRIM(RTRIM({self._quote_identifier(category_column)})) AS Categoria, Nombre
            FROM PRODUCTOS
            WHERE {self._quote_identifier(category_column)} IS NOT NULL
              AND LTRIM(RTRIM({self._quote_identifier(category_column)})) <> ''
            ORDER BY
                CASE LTRIM(RTRIM({self._quote_identifier(category_column)}))
                    WHEN 'Sushi' THEN 1
                    WHEN 'Fritos' THEN 2
                    WHEN 'Postres' THEN 3
                    WHEN 'Bebidas' THEN 4
                    ELSE 99
                END,
                Nombre
            """
        )
        catalog = {}
        for row in cursor.fetchall():
            catalog.setdefault(str(row.Categoria), []).append(row.Nombre)
        cursor.execute(
            """
            SELECT pp.NombreProd, SUM(pp.Cantidad) AS TotalVendido
            FROM PRODPED pp
            INNER JOIN PEDIDOS p ON p.IDPed = pp.IDPed
            WHERE p.Hora >= ? AND p.Hora < DATEADD(day, 1, ?)
            GROUP BY pp.NombreProd
            """,
            (inicio, fin),
        )
        ventas = {row.NombreProd: int(row.TotalVendido or 0) for row in cursor.fetchall()}
        result = []
        for categoria in ("Sushi", "Fritos", "Postres", "Bebidas"):
            productos = catalog.get(categoria, [])
            items = [{"nombre": nombre, "total": ventas.get(nombre, 0)} for nombre in productos]
            items.sort(key=lambda item: (item["total"], item["nombre"]), reverse=True)
            result.append({"categoria": categoria, "items": items})
        for categoria in [c for c in sorted(catalog.keys()) if c not in {"Sushi", "Fritos", "Postres", "Bebidas"}]:
            productos = catalog.get(categoria, [])
            items = [{"nombre": nombre, "total": ventas.get(nombre, 0)} for nombre in productos]
            items.sort(key=lambda item: (item["total"], item["nombre"]), reverse=True)
            result.append({"categoria": categoria, "items": items})
        return result

    def _get_category_column(self, cursor):
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'PRODUCTOS'
              AND COLUMN_NAME IN ('Categorias', 'Categoria')
            ORDER BY CASE COLUMN_NAME WHEN 'Categorias' THEN 0 ELSE 1 END
            """
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def _quote_identifier(self, name):
        return f"[{name}]"

    def _fetch_ingresos_mensuales(self, cursor, inicio, fin):
        cursor.execute(
            """
            SELECT YEAR(Hora) AS anio, MONTH(Hora) AS mes, SUM(PrecioTotal) AS ingresos
            FROM PEDIDOS
            WHERE Hora >= ? AND Hora < DATEADD(day, 1, ?)
            GROUP BY YEAR(Hora), MONTH(Hora)
            ORDER BY YEAR(Hora), MONTH(Hora)
            """,
            (inicio, fin),
        )
        result = []
        for row in cursor.fetchall():
            result.append({"anio": int(row.anio), "mes": int(row.mes), "label": f"{int(row.mes):02d}/{int(row.anio)}", "ingresos": round(float(row.ingresos or 0), 2)})
        return result

    def _fetch_ingresos_diarios(self, cursor, inicio, fin):
        cursor.execute(
            """
            SELECT CAST(Hora AS date) AS dia, SUM(PrecioTotal) AS ingresos
            FROM PEDIDOS
            WHERE Hora >= ? AND Hora < DATEADD(day, 1, ?)
            GROUP BY CAST(Hora AS date)
            ORDER BY CAST(Hora AS date)
            """,
            (inicio, fin),
        )
        result = []
        for row in cursor.fetchall():
            day_value = row.dia
            label = day_value.strftime("%d/%m") if hasattr(day_value, "strftime") else str(day_value)
            result.append({"label": label, "ingresos": round(float(row.ingresos or 0), 2)})
        return result
