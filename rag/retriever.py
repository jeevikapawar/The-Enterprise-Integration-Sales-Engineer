# rag/retriever.py
import pickle
import numpy as np
import faiss
from pathlib import Path
from loguru import logger
from sentence_transformers import SentenceTransformer
from config import config


class CaseStudyRetriever:
    def __init__(self):
        self.model = SentenceTransformer(config.embedding_model)
        self.index_path = Path(config.faiss_index_path)
        self.index = None
        self.case_studies = []
        self._load_index()

    def _load_index(self) -> None:
        index_file = self.index_path / "case_studies.index"
        metadata_file = self.index_path / "case_studies_metadata.pkl"

        if not index_file.exists() or not metadata_file.exists():
            raise FileNotFoundError(
                "FAISS index not found. "
                "Run `python scripts/index_case_studies.py` first."
            )

        self.index = faiss.read_index(str(index_file))

        with open(metadata_file, "rb") as f:
            self.case_studies = pickle.load(f)

        logger.info(
            f"📚 Loaded FAISS index with "
            f"{len(self.case_studies)} case studies"
        )

    def _build_query_text(self, extracted_data: dict) -> str:
        parts = []

        for pp in extracted_data.get("pain_points", []):
            parts.append(pp.get("description", ""))
            parts.append(pp.get("title", ""))

        for tech in extracted_data.get("current_tech_stack", []):
            parts.append(tech.get("name", ""))

        for outcome in extracted_data.get("desired_outcomes", []):
            parts.append(outcome.get("goal", ""))

        client_info = extracted_data.get("client_info", {})
        parts.append(client_info.get("industry", ""))

        return " ".join(filter(None, parts))

    def retrieve(self, extracted_data: dict, top_k: int = 3) -> list:
        query_text = self._build_query_text(extracted_data)
        logger.info("🔎 Searching for similar case studies...")

        query_embedding = self.model.encode([query_text])
        query_embedding = np.array(query_embedding).astype("float32")
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.case_studies):
                study = self.case_studies[idx].copy()
                study["similarity_score"] = float(score)
                results.append(study)
                logger.info(
                    f"  Found: '{study.get('title')}' "
                    f"(similarity: {score:.3f})"
                )

        logger.success(f"✅ Retrieved {len(results)} matching case studies")
        return results