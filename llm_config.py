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

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.6,
            max_completion_tokens=800,
            include_reasoning=False
        )

        return response.choices[0].message.content


def create_llm():
    return GroqLiteLLM()
