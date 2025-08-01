import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_huggingface import HuggingFaceEndpoint  # ✅ Correct import

# ✅ Load .env
load_dotenv()

class TranslationAgent:
    """
    TranslationAgent uses HuggingFaceEndpoint with updated LangChain syntax to translate documents
    without any extra text.
    """

    def __init__(self):
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not token:
            raise ValueError("❌ HUGGINGFACEHUB_API_TOKEN is missing from environment.")

        # ✅ Pass temperature directly, NOT inside model_kwargs
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.1",
            huggingfacehub_api_token=token,
            temperature=0.2  # ✅ FIX: pass directly
        )

        # ✅ Clean prompt template
        self.template = PromptTemplate.from_template(
            "Translate the following into {language}. Only return the translated text.\n\n{text}"
        )

        # ✅ Updated runnable chain syntax
        self.chain: RunnableSequence = self.template | self.llm

    def translate(self, text: str, language: str) -> str:
        return self.chain.invoke({"text": text, "language": language})
