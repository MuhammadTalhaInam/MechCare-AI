from crewai.llms.base_llm import BaseLLM
import os
from groq import Groq


class GroqLiteLLM(BaseLLM):

    def __init__(self):
        super().__init__(
            model="openai/gpt-oss-20b",
            temperature=0.6,
            max_tokens=800
        )

        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set.")

        self.client = Groq(api_key=self.api_key)

    def call(
        self,
        messages,
        callbacks=None,
        available_functions=None,
        from_task=None,
        from_agent=None,
        response_model=None,
        **kwargs
    ):

        # Remove CrewAI's unsupported cache_breakpoint
        clean_messages = []

        for message in messages:
            clean_message = dict(message)

            if "cache_breakpoint" in clean_message:
                del clean_message["cache_breakpoint"]

            clean_messages.append(clean_message)

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=clean_messages
        )

        return response.choices[0].message.content


def create_llm():
    return GroqLiteLLM()
