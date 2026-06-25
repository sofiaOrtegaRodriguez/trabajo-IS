import os
import re
import unicodedata
from datetime import date, datetime
from math import ceil

from src.modelo.dao.ProductoDaoJDBC import ProductoDaoJDBC
from src.modelo.dao.PromocionDaoJDBC import PromocionDaoJDBC


# ── Directorio raíz de /src (sube dos niveles desde este fichero)
_SRC_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
# ── Ruta por defecto a las imágenes de comida (se puede sobreescribir en los métodos)
_DEFAULT_IMAGE_ROOT = os.path.join(_SRC_DIR, "vista", "imagenes", "comida")


# ══════════════════════════════════════════════════════════════
#  Utilidades de matching imagen ↔ nombre de producto
# ══════════════════════════════════════════════════════════════

def _img_normalize(text):
    """
    Normalización fuerte: quita tildes/diacríticos, pasa a minúsculas
    y elimina todo lo que no sea alfanumérico.
    Ej: "Salmón Nigiri" → "salmonnigiri"
    """
    nfkd  = unicodedata.normalize("NFKD", str(text))
    ascii_ = nfkd.encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", ascii_.lower())


def _img_tokens(text):
    """
    Tokenización suave: separa por cualquier carácter no alfanumérico
    y descarta tokens de un solo carácter (artículos, etc.).
    Ej: "Coca-Cola Zero" → ["coca", "cola", "zero"]
    """
    nfkd  = unicodedata.normalize("NFKD", str(text))
    ascii_ = nfkd.encode("ascii", "ignore").decode().lower()
    return [t for t in re.split(r"[^a-z0-9]+", ascii_) if len(t) > 1]


def _img_score(stem, nombre):
    """
    Devuelve una puntuación 0-130 de cuánto coincide el stem del archivo
    con el nombre del producto. Mayor puntuación = mejor coincidencia.

    Lógica:
      - Coincidencia exacta normalizada → 130 (máximo, para inmediatamente)
      - Intersección de tokens → precision + recall promediados → 0-50
      - Bonus +30 si uno contiene al otro como subcadena
    """
    stem_norm   = _img_normalize(stem)
    nombre_norm = _img_normalize(nombre)
    if not stem_norm or not nombre_norm:
        return 0

    # Coincidencia exacta tras normalizar (caso más común y rápido)
    if stem_norm == nombre_norm:
        return 130

    stem_tok   = set(_img_tokens(stem))
    nombre_tok = set(_img_tokens(nombre))
    if not stem_tok or not nombre_tok:
        return 0

    comunes   = stem_tok & nombre_tok
    if not comunes:
        return 0

    precision = len(comunes) / len(stem_tok)    # ¿cuántos tokens del fichero están en el nombre?
    recall    = len(comunes) / len(nombre_tok)  # ¿cuántos tokens del nombre están en el fichero?
    score     = (precision + recall) / 2 * 50  # media armónica escalada a 0-50

    # Bonus por contención de subcadena (ej. fichero "salmon.jpg" y producto "Salmón Maki")
    if stem_norm in nombre_norm or nombre_norm in stem_norm:
        score += 30

    return score


# Puntuación mínima para que un fichero se considere imagen válida de un producto.
# Bajar este umbral = más falsos positivos; subirlo = más productos sin imagen.
_SCORE_UMBRAL = 40


# ══════════════════════════════════════════════════════════════
#  ServicioCarta  –  capa de servicio (Facade) para la carta
# ══════════════════════════════════════════════════════════════
class ServicioCarta:
    """
    Encapsula toda la lógica de negocio de la carta:
      - Filtrado por stock y disponibilidad
      - Aplicación de promociones activas
      - Paginación
      - Resolución de imágenes por nombre
      - Preparación del dict de render que consume CartaUI

    El controlador llama a obtenerProductosCategoriaRender() y pasa
    el resultado directamente a CartaUI.mostrar_productos().
    """

    def __init__(self, logica):
        self._logica = logica   # Referencia a Logica.py (Facade principal); no se usa aún aquí
                                # pero se conserva para que el controlador pueda delegar.

    # ── API pública ───────────────────────────────────────────

    def listarProductosCarta(self):
        """
        Devuelve un dict {categoria: [product_info, …]} con todos los productos
        visibles (stock > 0, disponible = Y) agrupados por categoría.
        Los productos con promoción activa van TAMBIÉN a la categoría 'promociones'.
        """
        grouped = {"sushi": [], "fritos": [], "bebidas": [], "postres": [], "promociones": []}
        productos           = self._listar_productos()
        promociones_activas = self._promociones_activas_por_producto()

        for producto in productos:
            # Filtro 1: stock mínimo de 1 unidad
            if int(getattr(producto, "stock", 0) or 0) < 1:
                continue
            # Filtro 2: campo disponible interpretado como booleano
            if not self._producto_disponible(producto.disponible):
                continue

            categoria = self._normalize_category(producto.categoria)
            if categoria not in grouped:
                continue  # Categoría desconocida → se ignora

            product_info = {
                "id":                   producto.nombre,   # El nombre actúa como ID único
                "nombre":               producto.nombre,
                "precio":               float(producto.precio),
                "categoria":            categoria,
                "precio_original":      float(producto.precio),
                "promocion_hasta":      "",
                "promocion_descuento":  0,
            }

            promo = promociones_activas.get(producto.nombre)
            if promo is not None:
                # Aplica el descuento y rellena los campos de promoción
                discounted_price = round(float(producto.precio) * (100 - float(promo.descuento)) / 100, 2)
                product_info["precio"]              = discounted_price
                product_info["precio_original"]     = float(producto.precio)
                product_info["promocion_hasta"]     = self._format_date(promo.fecha_fin)
                product_info["promocion_descuento"] = int(promo.descuento)
                grouped["promociones"].append(product_info)   # Va a promociones en lugar de su categoría
            else:
                grouped[categoria].append(product_info)

        return grouped

    def contarProductosCategoria(self, categoria):
        """Número de productos visibles en una categoría (útil para calcular páginas)."""
        return len(self._obtener_catalogo_categoria(categoria))

    def totalPaginasCategoria(self, categoria, por_pagina=4):
        """Número total de páginas para una categoría con el tamaño de página dado."""
        total     = self.contarProductosCategoria(categoria)
        por_pagina = max(1, int(por_pagina))
        return max(1, ceil(total / por_pagina))   # Siempre al menos 1 página

    def obtenerProductosCategoriaPaginados(self, categoria, pagina_actual, por_pagina=4):
        """
        Devuelve un dict con metadatos de paginación y el slice de productos
        correspondiente a la página solicitada.
        La página se normaliza automáticamente (nunca < 1 ni > total_paginas).
        """
        categoria  = str(categoria).strip().lower()
        por_pagina = max(1, int(por_pagina))
        total      = self.contarProductosCategoria(categoria)
        total_paginas  = max(1, self.totalPaginasCategoria(categoria, por_pagina))
        pagina_actual  = self._normalizar_pagina(pagina_actual, total_paginas)
        catalogo       = self._obtener_catalogo_categoria(categoria)
        inicio = (pagina_actual - 1) * por_pagina
        fin    = inicio + por_pagina
        return {
            "categoria":        categoria,
            "pagina_actual":    pagina_actual,
            "total_paginas":    total_paginas,
            "total_productos":  total,
            "productos":        list(catalogo[inicio:fin]),
        }

    def obtenerProductosCategoriaRender(self, categoria, pagina_actual, por_pagina=4, cesta=None, image_root=None):
        """
        Método principal que usa el controlador.
        Combina paginación + resolución de imágenes + formato de render
        y devuelve un dict listo para pasar a CartaUI.mostrar_productos().

        Parámetros:
          cesta      – callable(product_id) → int con la cantidad en cesta, o None
          image_root – ruta alternativa a las imágenes (tests, entornos distintos)

        Claves del dict devuelto:
          categoria, pagina_actual, total_paginas,
          productos_render  → lista de dicts para ProductCard
          catalogo_por_id   → {id: dict} para actualizar cantidades individuales
          info_pagina       → texto "Página X / Y" para el label
        """
        resultado     = self.obtenerProductosCategoriaPaginados(categoria, pagina_actual, por_pagina)
        resolved_root = image_root if image_root else _DEFAULT_IMAGE_ROOT

        # Resuelve rutas de imagen para los productos de esta página
        catalogo = self._resolver_rutas_imagen(
            {resultado["categoria"]: resultado["productos"]},
            image_root=resolved_root,
        )
        productos_render = self._preparar_productos_render(catalogo, cesta=cesta)
        info_pagina      = f"Página {resultado['pagina_actual']} / {resultado['total_paginas']}"
        catalogo_por_id  = {producto["id"]: producto for producto in productos_render}

        return {
            "categoria":        resultado["categoria"],
            "pagina_actual":    resultado["pagina_actual"],
            "total_paginas":    resultado["total_paginas"],
            "productos_render": productos_render,
            "catalogo_por_id":  catalogo_por_id,
            "info_pagina":      info_pagina,
        }

    # ── Métodos privados ──────────────────────────────────────

    def _obtener_catalogo_categoria(self, categoria):
        """Devuelve la lista de productos de una categoría del catálogo completo."""
        catalogo = self.listarProductosCarta()
        return list(catalogo.get(str(categoria).strip().lower(), []))

    def _normalizar_pagina(self, pagina_actual, total_paginas):
        """Garantiza que la página esté en el rango [1, total_paginas]."""
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
        """Delega la consulta a la BD al DAO correspondiente."""
        return ProductoDaoJDBC().listar()

    def _promociones_activas_por_producto(self):
        """
        Devuelve un dict {nombre_producto: Promocion} con la promoción
        más reciente (fecha_fin más lejana) que sigue vigente hoy.
        Si un producto tiene varias promos activas, gana la de mayor fecha_fin.
        """
        today           = date.today()
        promos_by_product = {}

        for promocion in PromocionDaoJDBC().listar():
            if not promocion.nombre_producto:
                continue
            fecha_fin = self._coerce_date(promocion.fecha_fin)
            if fecha_fin is None or fecha_fin < today:
                continue  # Promoción caducada o sin fecha → se ignora

            current = promos_by_product.get(promocion.nombre_producto)
            if current is None:
                promos_by_product[promocion.nombre_producto] = promocion
                continue

            # Si ya había una promo para ese producto, conserva la más larga
            current_fecha_fin = self._coerce_date(current.fecha_fin)
            if current_fecha_fin is None or fecha_fin > current_fecha_fin:
                promos_by_product[promocion.nombre_producto] = promocion

        return promos_by_product

    def _normalize_category(self, categoria):
        """
        Normaliza el valor de categoría que viene de la BD.
        Incluye alias para variaciones comunes (ej. "bebida" → "bebidas").
        Si la categoría es desconocida devuelve "" para que se filtre después.
        """
        normalized = str(categoria).strip().lower()
        aliases = {
            "sushi":   "sushi",
            "fritos":  "fritos",
            "postres": "postres",
            "bebidas": "bebidas",
            "bebida":  "bebidas",   # alias: singular → plural
        }
        return aliases.get(normalized, "")

    def _producto_disponible(self, disponible):
        """
        Interpreta el campo 'disponible' de la BD como booleano.
        Acepta: Y, SI, S, YES, TRUE, 1 (case-insensitive).
        """
        return str(disponible).strip().upper() in ("Y", "SI", "S", "YES", "TRUE", "1")

    def _coerce_date(self, value):
        """
        Convierte a date cualquier tipo que pueda venir de la BD:
        date nativo, datetime, o string en varios formatos.
        Devuelve None si no se puede parsear.
        """
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
        """Formatea una fecha al estilo europeo DD/MM/YYYY para mostrar en la UI."""
        fecha = self._coerce_date(value)
        return "" if fecha is None else fecha.strftime("%d/%m/%Y")

    def _resolver_rutas_imagen(self, catalogo, image_root=None):
        """
        Para cada producto del catálogo, busca en disco el archivo de imagen
        que mejor coincida con su nombre usando _img_score().

        folder_map define en qué carpetas buscar según la categoría lógica.
        Nota: la carpeta física es "bebida" (singular) aunque la categoría sea "bebidas".

        Devuelve el mismo dict catalogo con la clave "imagen_path" añadida a cada producto
        (None si ningún fichero supera el umbral _SCORE_UMBRAL).
        """
        image_root = os.path.normpath(image_root or _DEFAULT_IMAGE_ROOT)
        folder_map = {
            "sushi":       ["sushi"],
            "fritos":      ["fritos"],
            "postres":     ["postres"],
            "bebidas":     ["bebida", "bebidas"],          # Busca en ambas por si acaso
            "promociones": ["sushi", "fritos", "postres", "bebida", "bebidas"],  # Busca en todo
        }

        def _find(categoria, nombre):
            """Encuentra el mejor fichero de imagen para (categoria, nombre)."""
            best_score = 0
            best_path  = None
            for folder in folder_map.get(categoria, [categoria]):
                folder_path = os.path.join(image_root, folder)
                if not os.path.isdir(folder_path):
                    continue
                for filename in os.listdir(folder_path):
                    full = os.path.join(folder_path, filename)
                    if not os.path.isfile(full):
                        continue
                    stem, _ = os.path.splitext(filename)   # "salmon_maki.jpg" → stem="salmon_maki"
                    score   = _img_score(stem, nombre)
                    if score > best_score:
                        best_score = score
                        best_path  = full
            return best_path if best_score >= _SCORE_UMBRAL else None

        resultado = {}
        for categoria, productos in catalogo.items():
            resultado[categoria] = []
            for p in productos:
                producto = dict(p)   # Copia para no mutar el original
                producto["imagen_path"] = _find(producto.get("categoria", ""), producto.get("nombre", ""))
                resultado[categoria].append(producto)
        return resultado

    def _preparar_productos_render(self, catalogo, cesta=None):
        """
        Transforma el catálogo interno en la lista de dicts que espera ProductCard:
          id, nombre, precio, precio_str, promo_texto, imagen_path, has_image, quantity

        'cesta' es un callable(product_id) → int que devuelve la cantidad actual en cesta.
        Si no se pasa, se asume 0 para todos los productos.
        """
        resultado = []
        cesta     = cesta or (lambda _pid: 0)   # Fallback: ningún producto en cesta

        for productos in catalogo.values():
            for p in productos:
                path = p.get("imagen_path")
                resultado.append({
                    "id":         p["id"],
                    "nombre":     p["nombre"],
                    "precio":     float(p["precio"]),
                    "precio_str": f"{p['precio']:.2f} EUR",
                    # Texto de promo solo si hay fecha de fin; vacío si no hay promo
                    "promo_texto": (
                        f"-{p.get('promocion_descuento', 0)}% hasta {p.get('promocion_hasta', '')}"
                        if p.get("promocion_hasta") else ""
                    ),
                    "imagen_path": path,
                    "has_image":   bool(path),
                    "quantity":    cesta(p["id"]),   # Cantidad actual en la cesta del cliente
                })
        return resultado