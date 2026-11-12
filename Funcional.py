"""Módulo Funcional - Equipo de Desarrollo 2 (Funcional)

Implementa la carga, parseo y persistencia de retos en problems.yaml
utilizando exclusivamente el paradigma funcional (funciones puras,
inmutabilidad y ausencia de clases).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


def resolver_ruta(ruta: str) -> Path:
    """Retorna una ruta absoluta normalizada a partir del directorio actual del script."""
    path = Path(ruta)
    return path if path.is_absolute() else Path(__file__).parent / path


def crear_reto(
    title: str,
    prompt: str,
    hints: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Función pura para validar y construir el diccionario inmutable de un reto."""
    if not title or not prompt:
        raise ValueError("El título y la consigna (prompt) son obligatorios.")

    return {
        "title": str(title).strip(),
        "prompt": str(prompt).strip(),
        "hints": [str(h).strip() for h in (hints or []) if str(h).strip()],
        "tags": [str(t).strip() for t in (tags or []) if str(t).strip()],
    }


def parsear_lineas_bloque(lineas: List[str]) -> Optional[Dict[str, Any]]:
    """Procesa las líneas de un bloque de texto y retorna un diccionario de reto."""
    datos: Dict[str, Any] = {}

    for linea in (l.strip() for l in lineas if l.strip()):
        if linea.startswith("TITULO:"):
            datos["title"] = linea[len("TITULO:"):].strip()
        elif linea.startswith("CONSIGNA:"):
            datos["prompt"] = linea[len("CONSIGNA:"):].strip()
        elif linea.startswith("PISTAS:"):
            datos["hints"] = [
                h.strip()
                for h in linea[len("PISTAS:"):].split("|")
                if h.strip()
            ]
        elif linea.startswith("TAGS:"):
            datos["tags"] = [
                t.strip()
                for t in linea[len("TAGS:"):].split(",")
                if t.strip()
            ]

    if "title" in datos and "prompt" in datos:
        return crear_reto(
            title=datos["title"],
            prompt=datos["prompt"],
            hints=datos.get("hints", []),
            tags=datos.get("tags", []),
        )
    return None


def cargar_desde_txt(txt_path: str = "preguntas.txt") -> List[Dict[str, Any]]:
    """Lee y parsea un archivo .txt transformando bloques de texto en diccionarios de retos."""
    path = resolver_ruta(txt_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de retos: {path}")

    contenido = path.read_text(encoding="utf-8")
    bloques = contenido.split("=== RETO ===")

    # Transformación funcional mediante comprensión declarativa
    retos = [
        reto
        for bloque in bloques
        if (reto := parsear_lineas_bloque(bloque.splitlines())) is not None
    ]
    return retos


def cargar_existentes(filepath: str = "problems.yaml") -> List[Dict[str, Any]]:
    """Lee los retos existentes en el archivo YAML de forma pura sin modificar el archivo."""
    path = resolver_ruta(filepath)
    if not path.exists():
        return []

    if yaml is None:
        raise RuntimeError("Se requiere pyyaml para leer el archivo.")

    with path.open("r", encoding="utf-8") as f:
        datos = yaml.safe_load(f)

    if not isinstance(datos, list):
        return []

    # Filtrado y normalización funcional
    return [
        crear_reto(
            title=item["title"],
            prompt=item["prompt"],
            hints=item.get("hints", []),
            tags=item.get("tags", []),
        )
        for item in datos
        if isinstance(item, dict) and "title" in item and "prompt" in item
    ]


def combinar_retos(
    existentes: List[Dict[str, Any]], nuevos: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Combina dos listas de retos de forma inmutable, evitando duplicados por título."""
    titulos_vistos = set()
    resultado: List[Dict[str, Any]] = []

    for reto in existentes + nuevos:
        titulo = reto.get("title")
        if titulo and titulo not in titulos_vistos:
            titulos_vistos.add(titulo)
            resultado.append(reto)

    return resultado


def guardar(retos: List[Dict[str, Any]], filepath: str = "problems.yaml") -> None:
    """Serializa la colección de retos en un archivo YAML."""
    if yaml is None:
        raise RuntimeError("Se requiere pyyaml para guardar los retos.")

    path = resolver_ruta(filepath)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            retos,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )


def cargar_preguntas(
    filepath: str = "problems.yaml", txt_path: str = "preguntas.txt"
) -> None:
    """Punto de entrada funcional: compone la lectura, combinación y persistencia."""
    existentes = cargar_existentes(filepath)
    nuevos = cargar_desde_txt(txt_path)
    combinados = combinar_retos(existentes, nuevos)
    guardar(combinados, filepath)

    print(
        f"[Funcional] Se han cargado exitosamente {len(combinados)} retos en {filepath} desde {txt_path}."
    )


if __name__ == "__main__":
    cargar_preguntas()

