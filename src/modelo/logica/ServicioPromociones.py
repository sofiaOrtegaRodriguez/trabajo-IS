from datetime import date, datetime
from src.modelo.dao.PromocionDaoJDBC import PromocionDaoJDBC
from src.modelo.dao.ProductoDaoJDBC import ProductoDaoJDBC


class ServicioPromociones:
    def listarPromociones(self):
        return PromocionDaoJDBC().listar()

    def prepararPromocionesVista(self, promociones=None):
        if promociones is None:
            promociones = self.listarPromociones()
        promociones_vista = []
        for promocion in promociones:
            promociones_vista.append({
                "id_promocion": promocion.id_promocion,
                "nombre_producto": promocion.nombre_producto,
                "descuento": promocion.descuento,
                "periodo_texto": f"{self._format_date(promocion.fecha_inicio)} - {self._format_date(promocion.fecha_fin)}",
            })
        return promociones_vista

    def crearPromocion(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        return PromocionDaoJDBC().crear(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def crearPromocionValidada(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        self._validar_promocion_datos(descuento, fecha_inicio, fecha_fin, nombre_producto)
        return self.crearPromocion(descuento, fecha_inicio, fecha_fin, nombre_producto)

    def eliminarPromocion(self, id_promocion):
        return PromocionDaoJDBC().eliminar(id_promocion)

    def _validar_promocion_datos(self, descuento, fecha_inicio, fecha_fin, nombre_producto):
        if int(descuento) < 0 or int(descuento) > 100:
            raise ValueError("El descuento debe estar entre 0 y 100.")
        if fecha_inicio is None or fecha_fin is None:
            raise ValueError("Debes indicar fechas validas para la promocion.")
        if fecha_fin <= fecha_inicio:
            raise ValueError("La fecha fin debe ser posterior a la fecha inicio.")
        if not str(nombre_producto).strip():
            raise ValueError("Debes indicar el producto al que se aplica la promocion.")
        productos = [producto.nombre for producto in ProductoDaoJDBC().listar()]
        if str(nombre_producto).strip() not in productos:
            raise ValueError("El producto indicado no existe en la base de datos.")

    def _coerce_date(self, value):
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    def _format_date(self, value):
        fecha = self._coerce_date(value)
        return "" if fecha is None else fecha.strftime("%d/%m/%Y")
