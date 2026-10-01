
from crewai.llms.base_llm import BaseLLM
from google.colab import userdata
import litellm


class GroqLiteLLM(BaseLLM):

    def __init__(self):
        super().__init__(
            model="groq/openai/gpt-oss-20b",
            temperature=0.2,
            max_tokens=800
        )

        self.api_key = userdata.get("GROQ_API_KEY")

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

        response = litellm.completion(
            model=self.model,
            messages=messages,
            api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.content


def create_llm():
    return GroqLiteLLM()
