from app.prompting.loader import PromptLoader
from app.prompting.renderer import PromptRenderer


def test_prompt_loader_reads_markdown_prompt_from_disk(tmp_path) -> None:
    prompt_file = tmp_path / "translation" / "system.md"
    prompt_file.parent.mkdir(parents=True)
    prompt_file.write_text("translation system prompt", encoding="utf-8")

    loader = PromptLoader(base_dir=tmp_path)

    assert loader.load("translation/system.md") == "translation system prompt"


def test_prompt_renderer_formats_prompt_variables(tmp_path) -> None:
    prompt_file = tmp_path / "translation" / "feedback" / "grammar_error.md"
    prompt_file.parent.mkdir(parents=True)
    prompt_file.write_text("Issue={issue};Suggestion={suggestion}", encoding="utf-8")

    renderer = PromptRenderer(PromptLoader(base_dir=tmp_path))

    rendered = renderer.render(
        "translation/feedback/grammar_error.md",
        issue="时态错误",
        suggestion="went",
    )

    assert rendered == "Issue=时态错误;Suggestion=went"
