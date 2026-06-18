import os
import re
import unicodedata
from datetime import date, datetime
from math import ceil

from src.modelo.dao.ProductoDaoJDBC import ProductoDaoJDBC
from src.modelo.dao.PromocionDaoJDBC import PromocionDaoJDBC


_SRC_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
_DEFAULT_IMAGE_ROOT = os.path.join(_SRC_DIR, "vista", "imagenes", "comida")


def _img_normalize(text):
    """Quita tildes/diacríticos, pasa a minúsculas, deja solo alfanumérico."""
    nfkd = unicodedata.normalize("NFKD", str(text))
    ascii_ = nfkd.encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", ascii_.lower())


def _img_tokens(text):
    """Tokeniza por separadores no-alfanuméricos, descarta tokens de 1 carácter."""
    nfkd = unicodedata.normalize("NFKD", str(text))
    ascii_ = nfkd.encode("ascii", "ignore").decode().lower()
    return [t for t in re.split(r"[^a-z0-9]+", ascii_) if len(t) > 1]


def _img_score(stem, nombre):
    """
    Devuelve una puntuación 0-130 de cuánto coincide el stem del archivo
    con el nombre del producto. Mayor puntuación = mejor coincidencia.
    """
    stem_norm = _img_normalize(stem)
    nombre_norm = _img_normalize(nombre)
    if not stem_norm or not nombre_norm:
        return 0
    # Coincidencia exacta tras normalizar
    if stem_norm == nombre_norm:
        return 130
    stem_tok = set(_img_tokens(stem))
    nombre_tok = set(_img_tokens(nombre))
    if not stem_tok or not nombre_tok:
        return 0
    comunes = stem_tok & nombre_tok
    if not comunes:
        return 0
    precision = len(comunes) / len(stem_tok)
    recall = len(comunes) / len(nombre_tok)
    score = (precision + recall) / 2 * 50  # 0-50
    if stem_norm in nombre_norm or nombre_norm in stem_norm:
        score += 30
    return score


_SCORE_UMBRAL = 40  # puntuación mínima para considerar una coincidencia válida


class ServicioCarta:
    def __init__(self, logica):
        self._logica = logica

    def listarProductosCarta(self):
        grouped = {"sushi": [], "fritos": [], "bebidas": [], "postres": [], "promociones": []}
        productos = self._listar_productos()
        promociones_activas = self._promociones_activas_por_producto()

        for producto in productos:
            if int(getattr(producto, "stock", 0) or 0) < 1:
                continue
            if not self._producto_disponible(producto.disponible):
                continue
            categoria = self._normalize_category(producto.categoria)
            if categoria not in grouped:
                continue
            product_info = {
                "id": producto.nombre,
                "nombre": producto.nombre,
                "precio": float(producto.precio),
                "categoria": categoria,
                "precio_original": float(producto.precio),
                "promocion_hasta": "",
                "promocion_descuento": 0,
            }
            promo = promociones_activas.get(producto.nombre)
            if promo is not None:
                discounted_price = round(float(producto.precio) * (100 - float(promo.descuento)) / 100, 2)
                product_info["precio"] = discounted_price
                product_info["precio_original"] = float(producto.precio)
                product_info["promocion_hasta"] = self._format_date(promo.fecha_fin)
                product_info["promocion_descuento"] = int(promo.descuento)
                grouped["promociones"].append(product_info)
            else:
                grouped[categoria].append(product_info)
        return grouped

    def contarProductosCategoria(self, categoria):
        return len(self._obtener_catalogo_categoria(categoria))

    def totalPaginasCategoria(self, categoria, por_pagina=4):
        total = self.contarProductosCategoria(categoria)
        por_pagina = max(1, int(por_pagina))
        return max(1, ceil(total / por_pagina))

    def obtenerProductosCategoriaPaginados(self, categoria, pagina_actual, por_pagina=4):
        categoria = str(categoria).strip().lower()
        por_pagina = max(1, int(por_pagina))
        total = self.contarProductosCategoria(categoria)
        total_paginas = max(1, self.totalPaginasCategoria(categoria, por_pagina))
        pagina_actual = self._normalizar_pagina(pagina_actual, total_paginas)
        catalogo = self._obtener_catalogo_categoria(categoria)
        inicio = (pagina_actual - 1) * por_pagina
        fin = inicio + por_pagina
        return {
            "categoria": categoria,
            "pagina_actual": pagina_actual,
            "total_paginas": total_paginas,
            "total_productos": total,
            "productos": list(catalogo[inicio:fin]),
        }

    def obtenerProductosCategoriaRender(self, categoria, pagina_actual, por_pagina=4, cesta=None, image_root=None):
        resultado = self.obtenerProductosCategoriaPaginados(categoria, pagina_actual, por_pagina)
        resolved_root = image_root if image_root else _DEFAULT_IMAGE_ROOT
        catalogo = self._resolver_rutas_imagen(
            {resultado["categoria"]: resultado["productos"]},
            image_root=resolved_root,
        )
        productos_render = self._preparar_productos_render(catalogo, cesta=cesta)
        info_pagina = f"Página {resultado['pagina_actual']} / {resultado['total_paginas']}"
        catalogo_por_id = {producto["id"]: producto for producto in productos_render}
        return {
            "categoria": resultado["categoria"],
            "pagina_actual": resultado["pagina_actual"],
            "total_paginas": resultado["total_paginas"],
            "productos_render": productos_render,
            "catalogo_por_id": catalogo_por_id,
            "info_pagina": info_pagina,
        }

    def _obtener_catalogo_categoria(self, categoria):
        catalogo = self.listarProductosCarta()
        return list(catalogo.get(str(categoria).strip().lower(), []))

    def _normalizar_pagina(self, pagina_actual, total_paginas):
        try:
            pagina_actual = int(pagina_actual)
        except (TypeError, ValueError):
            pagina_actual = 1
        if pagina_actual < 1:
            return 1
        if pagina_actual > total_paginas:
            return total_paginas
        return pagina_actual

    def _listar_productos(self):
        return ProductoDaoJDBC().listar()

    def _promociones_activas_por_producto(self):
        today = date.today()
        promos_by_product = {}
        for promocion in PromocionDaoJDBC().listar():
            if not promocion.nombre_producto:
                continue
            fecha_fin = self._coerce_date(promocion.fecha_fin)
            if fecha_fin is None or fecha_fin < today:
                continue
            current = promos_by_product.get(promocion.nombre_producto)
            if current is None:
                promos_by_product[promocion.nombre_producto] = promocion
                continue
            current_fecha_fin = self._coerce_date(current.fecha_fin)
            if current_fecha_fin is None or fecha_fin > current_fecha_fin:
                promos_by_product[promocion.nombre_producto] = promocion
        return promos_by_product

    def _normalize_category(self, categoria):
        normalized = str(categoria).strip().lower()
        aliases = {
            "sushi": "sushi", "fritos": "fritos", "postres": "postres",
            "bebidas": "bebidas", "bebida": "bebidas",
        }
        return aliases.get(normalized, "")

    def _producto_disponible(self, disponible):
        return str(disponible).strip().upper() in ("Y", "SI", "S", "YES", "TRUE", "1")

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

    def _resolver_rutas_imagen(self, catalogo, image_root=None):
        image_root = os.path.normpath(image_root or _DEFAULT_IMAGE_ROOT)
        # La carpeta física es "bebida" (singular), la categoría lógica es "bebidas"
        folder_map = {
            "sushi": ["sushi"],
            "fritos": ["fritos"],
            "postres": ["postres"],
            "bebidas": ["bebida", "bebidas"],
            "promociones": ["sushi", "fritos", "postres", "bebida", "bebidas"],
        }

        def _find(categoria, nombre):
            best_score = 0
            best_path = None
            for folder in folder_map.get(categoria, [categoria]):
                folder_path = os.path.join(image_root, folder)
                if not os.path.isdir(folder_path):
                    continue
                for filename in os.listdir(folder_path):
                    full = os.path.join(folder_path, filename)
                    if not os.path.isfile(full):
                        continue
                    stem, _ = os.path.splitext(filename)
                    score = _img_score(stem, nombre)
                    if score > best_score:
                        best_score = score
                        best_path = full
            return best_path if best_score >= _SCORE_UMBRAL else None

        resultado = {}
        for categoria, productos in catalogo.items():
            resultado[categoria] = []
            for p in productos:
                producto = dict(p)
                producto["imagen_path"] = _find(producto.get("categoria", ""), producto.get("nombre", ""))
                resultado[categoria].append(producto)
        return resultado

    def _preparar_productos_render(self, catalogo, cesta=None):
        resultado = []
        cesta = cesta or (lambda _pid: 0)
        for productos in catalogo.values():
            for p in productos:
                path = p.get("imagen_path")
                resultado.append({
                    "id": p["id"],
                    "nombre": p["nombre"],
                    "precio": float(p["precio"]),
                    "precio_str": f"{p['precio']:.2f} EUR",
                    "promo_texto": (
                        f"-{p.get('promocion_descuento', 0)}% hasta {p.get('promocion_hasta', '')}"
                        if p.get("promocion_hasta") else ""
                    ),
                    "imagen_path": path,
                    "has_image": bool(path),
                    "quantity": cesta(p["id"]),
                })
        return resultado
