# scripts/index_case_studies.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from rag.embedder import CaseStudyEmbedder


def main():
    logger.info("🚀 Starting case study indexing...")
    embedder = CaseStudyEmbedder()
    embedder.build_index()
    logger.success("🎉 Indexing complete! You can now run the agent.")


if __name__ == "__main__":
    main()