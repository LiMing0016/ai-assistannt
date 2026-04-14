from app.prompting.loader import PromptLoader


class PromptRenderer:
    def __init__(self, loader: PromptLoader) -> None:
        self._loader = loader

    def render(self, prompt_name: str, **variables: str) -> str:
        template = self._loader.load(prompt_name)
        return template.format_map(_SafeFormatDict(variables))


class _SafeFormatDict(dict[str, str]):
    def __missing__(self, key: str) -> str:
        raise KeyError(f"Missing prompt variable: {key}")
