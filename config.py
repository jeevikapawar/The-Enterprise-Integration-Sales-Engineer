# config.py
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Config(BaseModel):
    # Claude
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Paths
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    case_studies_path: str = os.getenv("CASE_STUDIES_PATH", "./data/case_studies")
    output_dir: str = os.getenv("OUTPUT_DIR", "./output")
    prompts_dir: str = "./prompts"

    # Output
    output_format: str = os.getenv("OUTPUT_FORMAT", "markdown")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

config = Config()