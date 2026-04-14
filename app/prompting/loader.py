from functools import lru_cache
from pathlib import Path


class PromptLoader:
    def __init__(self, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir)

    def load(self, prompt_name: str) -> str:
        return self._load_cached(str(self._base_dir), prompt_name)

    @staticmethod
    @lru_cache(maxsize=128)
    def _load_cached(base_dir: str, prompt_name: str) -> str:
        prompt_path = Path(base_dir) / prompt_name
        return prompt_path.read_text(encoding="utf-8").strip()
