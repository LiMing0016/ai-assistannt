import math
import re

from app.state.models import ConversationMessage


MODEL_CONTEXT_WINDOWS: dict[tuple[str, str], int] = {
    ("openai", "gpt-5-mini"): 400_000,
    ("kimi", "moonshot-v1-8k"): 8_192,
    ("dashscope", "qwen-plus"): 131_072,
}

DEFAULT_CONTEXT_WINDOWS: dict[str, int] = {
    "openai": 128_000,
    "kimi": 8_192,
    "dashscope": 131_072,
}


def resolve_context_window(provider: str | None, model: str | None) -> int:
    normalized_provider = provider or "unknown"
    if provider and model and (provider, model) in MODEL_CONTEXT_WINDOWS:
        return MODEL_CONTEXT_WINDOWS[(provider, model)]
    if model:
        shorthand_match = re.search(r"(\d+)\s*[kK]\b", model)
        if shorthand_match:
            return int(shorthand_match.group(1)) * 1024
    return DEFAULT_CONTEXT_WINDOWS.get(normalized_provider, 32_768)


def estimate_text_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 2))


def estimate_message_tokens(role: str, content: str) -> int:
    return 4 + estimate_text_tokens(role) + estimate_text_tokens(content)


def reserve_output_tokens(context_window: int) -> int:
    return min(max(1_024, context_window // 8), 16_384)


def build_chat_messages(
    system_prompt: str,
    history_messages: list[ConversationMessage],
    current_message: str,
    provider: str | None,
    model: str | None,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    context_window = resolve_context_window(provider, model)
    output_reserve = reserve_output_tokens(context_window)
    input_budget = max(1_024, context_window - output_reserve)

    system_message = {"role": "system", "content": system_prompt}
    current_user_message = {"role": "user", "content": current_message}

    base_tokens = (
        estimate_message_tokens(system_message["role"], system_message["content"])
        + estimate_message_tokens(current_user_message["role"], current_user_message["content"])
    )

    selected_history: list[dict[str, str]] = []
    selected_history_count = 0
    running_tokens = base_tokens

    for history_message in reversed(history_messages):
        candidate_tokens = estimate_message_tokens(history_message.role, history_message.content)
        if selected_history and running_tokens + candidate_tokens > input_budget:
            break
        if not selected_history and running_tokens + candidate_tokens > input_budget:
            continue
        selected_history.append(
            {
                "role": history_message.role,
                "content": history_message.content,
            }
        )
        selected_history_count += 1
        running_tokens += candidate_tokens

    selected_history.reverse()
    trimmed_history_count = max(0, len(history_messages) - selected_history_count)

    return (
        [system_message, *selected_history, current_user_message],
        {
            "history_messages_loaded": selected_history_count,
            "history_messages_trimmed": trimmed_history_count,
            "context_window_tokens": context_window,
            "input_budget_tokens": input_budget,
            "estimated_input_tokens": running_tokens,
        },
    )
