from pathlib import Path
from typing import Any, Dict

import yaml

from dba.models.response_model import Response


class YamlService:
    def __init__(self, path: str | Path):
        self._path = Path(path)

    def load(self) -> Response[Dict[str, Any]]:
        try:
            with self._path.open("r") as f:
                data = yaml.safe_load(f) or {}
            return Response.success(data=data)
        except Exception as e:
            return Response.failure(message=f"Could not load {self._path}", error=e)

    def get(self, *keys: str) -> Any:
        """Retrieve nested keys (e.g., service.get('partman', 'my_table'))."""
        response: Response[Dict[str, Any]] = self.load()
        if not response.success or response.data is None:
            return None

        data = response.data
        for key in keys:
            if not isinstance(data, dict):
                return None
            data = data.get(key)
            if data is None:
                return None

        return data
