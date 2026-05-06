"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from multi_agent_research_lab.core.errors import StudentTodoError


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        import os
        from openai import Client
        from multi_agent_research_lab.core.config import get_settings

        settings = get_settings()
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "mock")
        if api_key == "mock":
            return LLMResponse(content="Mock LLM response for: " + user_prompt[:50] + "...", input_tokens=10, output_tokens=10, cost_usd=0.0)

        client = Client(api_key=api_key)
        
        # Enable LangSmith tracing for OpenAI calls
        if os.getenv("LANGCHAIN_TRACING_V2") == "true":
            try:
                from langsmith import wrappers
                client = wrappers.wrap_openai(client)
            except ImportError:
                pass
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                timeout=settings.timeout_seconds,
            )
            content = response.choices[0].message.content or ""
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            # GPT-4o-mini approx cost
            cost_usd = (input_tokens * 0.15 / 1e6) + (output_tokens * 0.6 / 1e6)
            return LLMResponse(content=content, input_tokens=input_tokens, output_tokens=output_tokens, cost_usd=cost_usd)
        except Exception as e:
            return LLMResponse(content=f"Error calling LLM: {str(e)}")
