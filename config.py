"""
Configuration loader for Router-Free Unified Harness.
Loads environment variables from .env and initializes the LLM provider.
"""

import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-pro")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
TOP_P_VALUE = float(os.getenv("TOP_P_VALUE", "0.9"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
TIMEOUT = int(os.getenv("TIMEOUT", "300"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))


def get_llm():
    """
    Returns an initialized LangChain ChatModel instance.
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please paste your Gemini API key in the .env file."
        )

    # Set both standard env vars for Google GenAI libraries
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Map preview model names gracefully if needed
        model = MODEL_NAME
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
            top_p=TOP_P_VALUE,
            max_output_tokens=MAX_TOKENS,
            timeout=TIMEOUT,
            max_retries=MAX_RETRIES,
        )
        return llm
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Gemini model '{MODEL_NAME}': {e}")
