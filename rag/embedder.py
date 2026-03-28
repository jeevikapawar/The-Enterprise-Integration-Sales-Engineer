# rag/embedder.py
import json
import pickle
import numpy as np
import faiss
from pathlib import Path
from loguru import logger
from sentence_transformers import SentenceTransformer
from config import config


class CaseStudyEmbedder:
    def __init__(self):
        self.model = SentenceTransformer(config.embedding_model)
        self.index_path = Path(config.faiss_index_path)
        self.case_studies_path = Path(config.case_studies_path)
        self.index = None
        self.case_studies = []

    def load_case_studies(self) -> list:
        studies = []
        json_files = list(self.case_studies_path.glob("*.json"))

        if not json_files:
            raise FileNotFoundError(
                f"No case study JSON files found in {self.case_studies_path}"
            )

        for filepath in json_files:
            with open(filepath, "r") as f:
                study = json.load(f)
                studies.append(study)
                logger.info(f"  Loaded: {study.get('title', filepath.name)}")

        logger.success(f"✅ Loaded {len(studies)} case studies")
        return studies

    def _build_searchable_text(self, study: dict) -> str:
        parts = [
            study.get("title", ""),
            study.get("industry", ""),
            study.get("solution_summary", ""),
            study.get("architecture_pattern", ""),
            " ".join(study.get("pain_points", [])),
            " ".join(study.get("tags", [])),
            " ".join(study.get("technologies_used", [])),
            " ".join(study.get("outcomes", [])),
        ]
        return " ".join(filter(None, parts))

    def build_index(self) -> None:
        logger.info("🔨 Building FAISS index from case studies...")
        self.case_studies = self.load_case_studies()
        texts = [self._build_searchable_text(s) for s in self.case_studies]

        logger.info("🧠 Generating embeddings...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype("float32")
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        self.index_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(
            self.index,
            str(self.index_path / "case_studies.index")
        )

        with open(self.index_path / "case_studies_metadata.pkl", "wb") as f:
            pickle.dump(self.case_studies, f)

        logger.success(
            f"✅ FAISS index built with {len(self.case_studies)} "
            f"case studies → saved to {self.index_path}"
        )