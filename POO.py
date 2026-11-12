"""Módulo POO - Equipo de Desarrollo 1 (POO)

Implementa la representación orientada a objetos de retos/preguntas de programación
y la función cargar_preguntas() para poblar problems.yaml leyendo desde un archivo .txt.
"""

from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


class Reto:
    """Representa un reto o problema técnico de programación en Python."""

    def __init__(
        self,
        title: str,
        prompt: str,
        hints: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        if not title or not prompt:
            raise ValueError("El título y la consigna (prompt) son obligatorios.")

        self.title = str(title).strip()
        self.prompt = str(prompt).strip()
        self.hints = [str(h).strip() for h in hints] if hints is not None else []
        self.tags = [str(t).strip() for t in tags] if tags is not None else []

    def to_dict(self) -> Dict:
        """Serializa la instancia a un diccionario compatible con problems.yaml."""
        return {
            "title": self.title,
            "prompt": self.prompt,
            "hints": self.hints,
            "tags": self.tags,
        }

    def __repr__(self) -> str:
        return f"<Reto '{self.title}'>"


class BancoRetosPOO:
    """Administra la colección de retos, su carga dinámica y su persistencia en YAML."""

    def __init__(self, filepath: str = "problems.yaml") -> None:
        self.filepath = Path(filepath)
        if not self.filepath.is_absolute():
            self.filepath = Path(__file__).parent / self.filepath
        self.retos: List[Reto] = []

    def agregar_reto(self, reto: Reto) -> None:
        """Agrega un nuevo objeto Reto al banco si no existe ya un reto con el mismo título."""
        if not any(r.title == reto.title for r in self.retos):
            self.retos.append(reto)

    def cargar_existentes(self) -> None:
        """Carga retos existentes desde el archivo YAML para evitar pérdida de datos previos."""
        if not self.filepath.exists():
            return

        if yaml is None:
            raise RuntimeError("Se requiere pyyaml para leer el archivo.")

        with self.filepath.open("r", encoding="utf-8") as f:
            datos = yaml.safe_load(f)
            if not isinstance(datos, list):
                return
            for item in datos:
                if isinstance(item, dict) and "title" in item and "prompt" in item:
                    reto = Reto(
                        title=item["title"],
                        prompt=item["prompt"],
                        hints=item.get("hints", []),
                        tags=item.get("tags", []),
                    )
                    self.agregar_reto(reto)

    def guardar(self) -> None:
        """Persiste todos los retos almacenados en el archivo YAML."""
        if yaml is None:
            raise RuntimeError("Se requiere pyyaml para guardar los retos.")

        datos = [reto.to_dict() for reto in self.retos]
        with self.filepath.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                datos,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )

    @classmethod
    def cargar_desde_txt(cls, txt_path: str = "preguntas.txt") -> List[Reto]:
        """Lee y parsea un archivo .txt con retos estructurados e instancia objetos Reto."""
        path = Path(txt_path)
        if not path.is_absolute():
            path = Path(__file__).parent / path

        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de retos: {path}")

        contenido = path.read_text(encoding="utf-8")
        bloques = contenido.split("=== RETO ===")
        retos: List[Reto] = []

        for bloque in bloques:
            lineas = [linea.strip() for linea in bloque.splitlines() if linea.strip()]
            if not lineas:
                continue

            datos = {}
            for linea in lineas:
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
                retos.append(
                    Reto(
                        title=datos["title"],
                        prompt=datos["prompt"],
                        hints=datos.get("hints", []),
                        tags=datos.get("tags", []),
                    )
                )

        return retos


def cargar_preguntas(
    filepath: str = "problems.yaml", txt_path: str = "preguntas.txt"
) -> None:
    """Punto de entrada para cargar los retos desde el archivo .txt en el archivo YAML."""
    banco = BancoRetosPOO(filepath=filepath)
    banco.cargar_existentes()
    nuevos_retos = BancoRetosPOO.cargar_desde_txt(txt_path=txt_path)
    for reto in nuevos_retos:
        banco.agregar_reto(reto)
    banco.guardar()
    print(
        f"[POO] Se han cargado exitosamente {len(banco.retos)} retos en {filepath} desde {txt_path}."
    )


if __name__ == "__main__":
    cargar_preguntas()

