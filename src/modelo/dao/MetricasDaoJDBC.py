from datetime import date, datetime

#clase que proporcina la conexión y cursor de SQL SERVER
from src.modelo.conexion.ConexionSQLServer import ConexionSQLServer

#DAO = data access object encargado de obtener todas las métricas
#necesarias para el panel del gerente
class MetricasDaoJDBC(ConexionSQLServer):
    def obtener_metricas(self, fecha_inicio=None, fecha_fin=None):
        """
            metodo principal, obtiene todas las métricas necesasrias para mostrar en el
            dashboard:
                - Resumen general de pedidos e ingresos.
                - Distribución de empleados por tipo.
                - Productos agrupados por categoría.
                - Ingresos mensuales.
                - Ingresos diarios.

            Parámetros:
                fecha_inicio: fecha inicial del rango.
                fecha_fin: fecha final del rango.

            Si no se recibe fecha_inicio, se utiliza automáticamente
            desde el primer día del mes actual hasta hoy.

            LAS FUNCIONES/MÉTODOS QUE SE USAN SE DEFINEN LUEGO, MIRAD ABAJO CHICOS
        """
        #normaliza y valida el rango de las fechas
        inicio, fin = self._normalizar_rango(fecha_inicio, fecha_fin)
        #obtiene el cursor para ejecutar consultas SQL (a la BD)
        cursor = self.getCursor()
        try:
            #detecta si la tabla PRODUCTOS de la BD usa la columna "categoria" o "categorias"
            category_column = self._get_category_column(cursor)
            #obtiene estadísticas generales
            resumen = self._fetch_resumen(cursor, inicio, fin)
            #obtener num de empleados agrupados por tipo (cocina, cajero..)
            empleados = self._fetch_empleados(cursor)
            #obtiene prod. agrupados por categorias junto con las ventas realizadas
            categorias = self._fetch_productos_por_categoria(cursor, inicio, fin, category_column)
            #obtiene ingresos grouped by mes
            mensuales = self._fetch_ingresos_mensuales(cursor, inicio, fin)
            #lo mismo pero en vez mensual diario
            diarios = self._fetch_ingresos_diarios(cursor, inicio, fin)

            #toda esta información la devuelve en un diccionario
            return {"resumen": resumen, "empleados": empleados, "categorias": categorias, "mensuales": mensuales, "diarios": diarios, "inicio": inicio, "fin": fin}
        
        #en caso de error
        except Exception as exc:
            raise RuntimeError(f"No se pudieron cargar las metricas del gerente: {exc}") from exc
        
        #cierra el cursor (lo q se usa para hacer consultas SQL) siempre (independientemente si hay o no error)
        finally:
            if cursor is not None:
                cursor.close()
            self.closeConnection()

    ##NORMALIZAR RANGO#####################
    def _normalizar_rango(self, fecha_inicio, fecha_fin): 
        """
            convierte las fechas recibidas como parámetro de la clase (fecha_inicio y fecha_fin)
            en un rango válido.
            2 casos:
            
            1. Si no se recibe fecha_inicio:
                - Se toma fecha_fin (o hoy si tampoco existe).
                - Se usa como inicio el primer día del mismo mes.

            2. Si se recibe fecha_inicio:
                - Convierte ambas fechas a objetos date.
                - Si fecha_fin es menor que fecha_inicio,
                las intercambia para evitar rangos inválidos.

            Devuelve:
                (inicio, fin)
        """

        #aqui se puede ver los casos en código
        #si no hay fecha_inicio
        if fecha_inicio is None:
            fecha_fin = date.today() if fecha_fin is None else self._coerce_date(fecha_fin)
            return fecha_fin.replace(day=1), fecha_fin
        #si si que hay fecha_inicio
        inicio = self._coerce_date(fecha_inicio)
        fin = self._coerce_date(fecha_fin or fecha_inicio)
        #devuelce (inicio, fin)
        return (fin, inicio) if fin < inicio else (inicio, fin)

    #TIPO DE DATOS FECHA
    def _coerce_date(self, value):
        """
            permite pasar de diferentes formatos de fecha a un objeto date.
            es decir, pasa de -date, -datetime, -string con formato YYYY-MM-DD
            a un objeto del tipo date.

            Si recibe un formato NO válido lanza error
        """

        #si ya es tipo date devuelve el valor sin más
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        #si es tipo datetime convierte a date
        if isinstance(value, datetime):
            return value.date()
        #si es str convierte a date
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        
        #en cualquier otro caso error
        raise TypeError("Fecha no valida")

    #OBTENER MÉTRICAS GLOBALES
    def _fetch_resumen(self, cursor, inicio, fin):
        """
            Obtiene métricas globales del periodo:

            - Número total de pedidos.
            - Número de clientes distintos.
            - Ingresos totales.
            - Ingresos procedentes únicamente de pedidos asociados a clientes.

            El filtro:
                Hora >= inicio
                Hora < fin + 1 día

            permite incluir completamente el último día.
        """

        #codigo en SQL que se ejecuta como query en la BD
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
        return {
            "pedidos": int(getattr(row, "pedidos", 0) or 0), 
            "clientes": int(getattr(row, "clientes", 0) or 0), 
            "ingresos": round(float(getattr(row, "ingresos", 0) or 0), 2), 
            "ingresos_clientes": round(
                float(getattr(row, "ingresos_clientes", 0) or 0), 2)
        }

    #OBTENER EMPLEADOS
    def _fetch_empleados(self, cursor):
        """
            Cuenta cuántos empleados existen de cada tipo.

            Ejemplo:
                Cocinero -> 5
                Camarero -> 3
                Repartidor -> 2
        """
        #consulta SQL 
        cursor.execute(
            """
            SELECT Emp_Tipo, COUNT(*) AS total
            FROM EMPLEADOS
            GROUP BY Emp_Tipo
            ORDER BY Emp_Tipo
            """
        )
        return [
            {
                "tipo": row.Emp_Tipo,
                "total": int(row.total or 0)
            }
            for row in cursor.fetchall()
        ]


    #OBTENER PRODUCTOS POR CATEGORÍAS
    def _fetch_productos_por_categoria(self, cursor, inicio, fin, category_column):

        """
            Obtiene los productos agrupados por categoría
            y calcula cuántas unidades se han vendido
            dentro del rango de fechas seleccionado.
            Devuelve una estructura:
            [
                {
                    "categoria": "Sushi",
                    "items": [
                        {
                            "nombre": "...",
                            "total": ...
                        }
                    ] #AQUI LOS PRODUCTOS DE CADA CATEG.
                }
            ]
        """

        #si la tabla nni tiene col. categoría devuelcee genérica vacía
        if category_column is None:
            return [{"categoria": "Sin categoria", "items": []}]
        
        #obtiene todos los productos agrupados pro categoría
        #código SQL
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
        # Diccionario:
        # {
        #   categoria: [productos]
        # }
        catalog = {}
        #añadir al catálogo
        for row in cursor.fetchall():
            catalog.setdefault(str(row.Categoria), []).append(row.Nombre)

        # Obtiene ventas acumuladas por producto con SQL 
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
        # Diccionario:
        # {
        #   producto: total_vendido
        # }
        ventas = {row.NombreProd: int(row.TotalVendido or 0) for row in cursor.fetchall()}

        result = []
        #categorías que aparecen primero
        for categoria in ("Sushi", "Fritos", "Postres", "Bebidas"):
            productos = catalog.get(categoria, [])
            items = [
                {"nombre": nombre, 
                 "total": ventas.get(nombre, 0)} 
                for nombre in productos
            ]
            #ordenar de forma desc por ventas
            items.sort(
                key=lambda item: (
                    item["total"],
                    item["nombre"]
                    ), 
                    reverse=True
                )
            #se añade a resultados
            result.append({"categoria": categoria, "items": items})

        # Procesa cualquier otra categoría no contemplada pro si a futuro se añaden
        for categoria in [
            c for c in sorted(catalog.keys())
            if c not in {
                "Sushi",
                "Fritos",
                "Postres",
                "Bebidas"
            }
        ]:
            productos = catalog.get(categoria, [])

            items = [
                {
                    "nombre": nombre,
                    "total": ventas.get(nombre, 0)
                }
                for nombre in productos
            ]

            items.sort(
                key=lambda item: (
                    item["total"],
                    item["nombre"]
                ),
                reverse=True
            )

            result.append({
                "categoria": categoria,
                "items": items
            })

        return result

    #NOMBRE DE LA COLUMNA CATEGORÍA(S)
    def _get_category_column(self, cursor):
        """
            Comprueba qué nombre de columna existe
            en la tabla PRODUCTOS.

            Busca:
            - Categorias
            - Categoria

            Prioriza 'Categorias' si ambas existen.
        """
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
        """
            Encierra un identificador SQL entre corchetes.
            Ejemplo:
                Categoria -> [Categoria]
            Útil para evitar errores con nombres reservados.
        """
        return f"[{name}]"

    #INGRESOS MENSUALES
    def _fetch_ingresos_mensuales(self, cursor, inicio, fin):
        """
            Agrupa los ingresos por año y mes.

            Ejemplo:
                Enero 2025 -> 1500€
                Febrero 2025 -> 1800€
        """
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

    #INGRESOS DIARIOS
    def _fetch_ingresos_diarios(self, cursor, inicio, fin):
        """
            Agrupa los ingresos por día.

            Ejemplo:
                01/05 -> 120€
                02/05 -> 210€
        """
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
