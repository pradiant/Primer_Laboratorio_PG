"""Módulo bot - Chatbot de Retos de Programación

Carga y gestiona las preguntas técnicas desde problems.yaml,
con soporte para Slack Bot y manejo robusto de excepciones.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    WebClient = None
    SlackApiError = Exception


class PreguntasError(Exception):
    """Excepción base para errores relacionados con la carga y gestión de retos."""
    pass


class ArchivoRetosNoEncontradoError(PreguntasError):
    """Lanzada cuando el archivo problems.yaml no existe."""
    pass


class FormatoInvalidoRetosError(PreguntasError):
    """Lanzada cuando el archivo problems.yaml tiene un formato no válido."""
    pass


def cargar_preguntas(filepath: str = "problems.yaml") -> List[Dict[str, Any]]:
    """Carga y valida los retos técnicos desde un archivo YAML.

    Args:
        filepath: Ruta al archivo YAML con los retos.

    Returns:
        Lista de diccionarios con los retos.

    Raises:
        ArchivoRetosNoEncontradoError: Si el archivo no existe.
        FormatoInvalidoRetosError: Si el archivo no es un YAML válido o no es una lista.
    """
    path = Path(filepath)
    if not path.is_absolute():
        path = Path(__file__).parent / path

    if not path.exists():
        raise ArchivoRetosNoEncontradoError(
            f"El archivo de configuración {path} no fue encontrado."
        )

    try:
        with path.open("r", encoding="utf-8") as f:
            datos = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise FormatoInvalidoRetosError(
            f"Error al parsear el archivo YAML {path}: {exc}"
        ) from exc

    if not isinstance(datos, list):
        raise FormatoInvalidoRetosError(
            f"El archivo {path} debe contener una lista de retos en formato YAML."
        )

    return datos


class ChatbotRetos:
    """Chatbot encargado de administrar retos e interactuar con Slack."""

    def __init__(
        self,
        token: Optional[str] = None,
        filepath: str = "problems.yaml",
    ) -> None:
        self.token = token or os.environ.get("SLACK_BOT_TOKEN")
        self.filepath = filepath
        self.retos: List[Dict[str, Any]] = []
        self.client = WebClient(token=self.token) if WebClient and self.token else None
        self.cargar()

    def cargar(self) -> None:
        """Carga los retos técnicos manejando las posibles excepciones."""
        try:
            self.retos = cargar_preguntas(self.filepath)
            print(f"[Bot] Se cargaron {len(self.retos)} retos desde {self.filepath}.")
        except PreguntasError as error:
            print(f"[Bot Error] {error}")
            self.retos = []

    def enviar_reto(self, channel: str, indice: int = 0) -> Optional[Dict[str, Any]]:
        """Envía un reto a un canal de Slack."""
        if not self.retos:
            print("[Bot] No hay retos disponibles para enviar.")
            return None

        if indice < 0 or indice >= len(self.retos):
            print(f"[Bot] Índice de reto inválido: {indice}.")
            return None

        reto = self.retos[indice]
        mensaje = (
            f"*Reto:* {reto.get('title', 'Sin título')}\n\n"
            f"*Consigna:* {reto.get('prompt', '')}\n"
            f"*Tags:* {', '.join(reto.get('tags', []))}"
        )

        if not self.client:
            print(f"[Bot Simulación] Envío al canal {channel}:\n{mensaje}")
            return {"ok": True, "simulado": True, "message": mensaje}

        try:
            response = self.client.chat_postMessage(channel=channel, text=mensaje)
            return response
        except SlackApiError as e:
            print(f"[Bot Error] Error de Slack API al enviar mensaje: {e.response['error']}")
            return None


if __name__ == "__main__":
    bot = ChatbotRetos()
    print(f"Total de retos disponibles: {len(bot.retos)}")

