"""
CloudServe Intelligent Support Automation System package.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Sanitize environment variables to prevent quote wrapping issues with LangSmith / Gemini APIs
for env_key in ["LANGCHAIN_API_KEY", "GOOGLE_API_KEY", "LANGCHAIN_PROJECT", "LANGCHAIN_TRACING_V2", "LANGCHAIN_ENDPOINT"]:
    if env_key in os.environ and os.environ[env_key]:
        os.environ[env_key] = os.environ[env_key].strip("'\" ")

