from datetime import date, datetime
from src.modelo.dao.PromocionDaoJDBC import PromocionDaoJDBC
from src.modelo.dao.ProductoDaoJDBC import ProductoDaoJDBC

class ServicioPromociones:
    """
    Servicio de lógica de negocio para promociones.

    Esta clase pertenece a la CAPA DE LÓGICA (no es un DAO ni una vista).
    Actúa como intermediaria entre el controlador y los DAOs, y es la
    responsable de:
      - Obtener y transformar datos de promociones para la vista
      - Validar los datos antes de persistirlos
      - Delegar la persistencia en PromocionDaoJDBC y ProductoDaoJDBC

    No accede directamente a la BD: siempre lo hace a través de los DAOs.
    """

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PÚBLICOS: listado y preparación para la vista
    # ─────────────────────────────────────────────────────────────

    def listarPromociones(self):
        """
        Devuelve la lista de VOs de promoción tal como los entrega el DAO.
        Es una consulta directa sin transformación adicional.
        """
        return PromocionDaoJDBC().listar()

    def prepararPromocionesVista(self, promociones=None):
        """
        Transforma la lista de VOs de promoción en una lista de dicts
        listos para que la vista los renderice en la tabla.

        Si no se pasa una lista, las obtiene directamente de la BD.

        Cada dict de salida tiene:
          - "id_promocion":    identificador de la promoción
          - "nombre_producto": nombre del producto asociado
          - "descuento":       porcentaje de descuento (int)
          - "periodo_texto":   rango de fechas formateado "DD/MM/YYYY - DD/MM/YYYY"

        Esto separa la responsabilidad de formateo de la vista:
        la vista solo hace setText(), no formatea fechas.
        """
        if promociones is None:
            promociones = self.listarPromociones()

        promociones_vista = []
        for promocion in promociones:
            promociones_vista.append({
                "id_promocion": promocion.id_promocion,
                "nombre_producto": promocion.nombre_producto,
                "descuento": promocion.descuento,
                # _format_date convierte la fecha (sea date, datetime o str) a "DD/MM/YYYY"
                "periodo_texto": f"{self._format_date(promocion.fecha_inicio)} - {self._format_date(promocion.fecha_fin)}",
            })
        return promociones_vista

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PÚBLICOS: creación y eliminación
    # ─────────────────────────────────────────────────────────────

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        """
        Crea una promoción en la BD SIN validar los datos.
        Delega directamente en el DAO.

        Útil cuando el controlador ya ha validado previamente los datos
        o cuando se crean promociones desde un proceso interno.
        """
        return PromocionDaoJDBC().crear(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def crearPromocionValidada(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        """
        Valida los datos y, si son correctos, crea la promoción en la BD.

        Es el método que debe llamar el controlador cuando el usuario
        rellena el formulario y pulsa "Guardar promoción".

        Lanza ValueError con mensaje descriptivo si algún dato no es válido.
        """
        self._validar_promocion_datos(descuento, fecha_inicio, fecha_fin, nombre_producto)
        return self.crearPromocion(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def eliminarPromocion(self, id_promocion):
        """
        Elimina la promoción con el ID indicado.
        Delega directamente en el DAO sin validación adicional.
        """
        return PromocionDaoJDBC().eliminar(id_promocion)

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS: validación
    # ─────────────────────────────────────────────────────────────

    def _validar_promocion_datos(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        """
        Valida todos los campos del formulario de promoción.
        Lanza ValueError en el primer error encontrado.

        Reglas de validación:
          1. descuento debe ser un entero entre 0 y 100
          2. fecha_inicio y fecha_fin no pueden ser None
          3. fecha_fin debe ser estrictamente posterior a fecha_inicio
          4. nombre_producto no puede estar vacío
          5. nombre_producto debe existir en la tabla PRODUCTOS de la BD
        """
        # Regla 1: rango de descuento
        if int(descuento) < 0 or int(descuento) > 100:
            raise ValueError("El descuento debe estar entre 0 y 100.")

        # Regla 2: fechas no nulas
        if fecha_inicio is None or fecha_fin is None:
            raise ValueError("Debes indicar fechas validas para la promocion.")

        # Regla 3: fecha_fin posterior a fecha_inicio
        if fecha_fin <= fecha_inicio:
            raise ValueError("La fecha fin debe ser posterior a la fecha inicio.")

        # Regla 4: producto no vacío
        if not str(nombre_producto).strip():
            raise ValueError("Debes indicar el producto al que se aplica la promocion.")

        # Regla 5: el producto debe existir en la BD
        # Consulta los productos existentes y comprueba que el nombre indicado está entre ellos
        productos = [producto.nombre for producto in ProductoDaoJDBC().listar()]
        if str(nombre_producto).strip() not in productos:
            raise ValueError("El producto indicado no existe en la base de datos.")

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS: utilidades de fecha
    # ─────────────────────────────────────────────────────────────

    def _coerce_date(self, value):
        """
        Convierte cualquier representación de fecha a un objeto datetime.date.
        Devuelve None si la conversión no es posible.

        Casos que maneja:
          - date (pero no datetime): lo devuelve tal cual
          - datetime: extrae solo la parte de fecha con .date()
          - str: intenta los formatos "YYYY-MM-DD", "DD/MM/YYYY" y "YYYY-MM-DD HH:MM:SS"
          - cualquier otro tipo: devuelve None
        """
        # Si ya es un date puro (no subclase datetime), no hace falta conversión
        if isinstance(value, date) and not isinstance(value, datetime):
            return value

        # datetime es subclase de date, por eso se comprueba antes por separado
        if isinstance(value, datetime):
            return value.date()

        # Si es una cadena de texto, prueba los formatos más comunes
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue  # prueba el siguiente formato

        return None  # tipo desconocido o cadena con formato no reconocido

    def _format_date(self, value):
        """
        Formatea una fecha (de cualquier tipo soportado por _coerce_date)
        como cadena "DD/MM/YYYY" para mostrar en la vista.

        Devuelve "" si la fecha es None o no se puede convertir,
        evitando que la vista muestre "None" o rompa al hacer setText().
        """
        fecha = self._coerce_date(value)
        return "" if fecha is None else fecha.strftime("%d/%m/%Y")
    