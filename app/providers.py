import os
import abc
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "tinydolphin")

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

class OllamaProvider(LLMProvider):
    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model
    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.url, json={"model": self.model, "prompt": prompt, "stream": False}, timeout=120.0)
            resp.raise_for_status()
            return resp.json().get("response", "")

class AzureOpenAIProvider(LLMProvider):
    def __init__(self, endpoint: str, key: str, deployment: str):
        self.endpoint = endpoint
        self.headers = {"api-key": key, "Content-Type": "application/json"}
        self.url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview"
    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            payload = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 800}
            resp = await client.post(self.url, headers=self.headers, json=payload, timeout=60.0)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

class AWSBedrockProvider(LLMProvider):
    def __init__(self, region: str):
        self.region = region
    async def generate(self, prompt: str) -> str:
        return "AWS Bedrock Mock Response"

def get_provider() -> LLMProvider:
    target = os.getenv("UPSTREAM_PROVIDER", "OLLAMA").upper()
    if target == "AZURE":
        return AzureOpenAIProvider(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            key=os.getenv("AZURE_OPENAI_KEY", ""),
            deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        )
    elif target == "AWS":
        return AWSBedrockProvider(region=os.getenv("AWS_REGION", "us-east-1"))
    return OllamaProvider(url=OLLAMA_URL, model=MODEL_NAME)