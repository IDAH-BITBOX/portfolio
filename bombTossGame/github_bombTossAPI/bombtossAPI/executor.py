from jina import Executor, requests
from docarray import DocList, BaseDoc

from transformers import pipeline


class Prompt(BaseDoc):
    text: str


class Generation(BaseDoc):
    prompt: str
    text: str


class StableLM(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.generator = pipeline(
            'text-generation', model='stabilityai/stablelm-base-alpha-3b'
        )

    @requests
    def generate(self, docs: DocList[Prompt], **kwargs) -> DocList[Generation]:
        generations = DocList[Generation]()
        prompts = docs.text
        llm_outputs = self.generator(prompts)
        for prompt, output in zip(prompts, llm_outputs):
            generations.append(Generation(prompt=prompt, text=output))
        return generations