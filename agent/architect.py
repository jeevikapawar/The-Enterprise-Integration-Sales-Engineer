# agent/architect.py
import json
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
import google.generativeai as genai
from config import config
from agent.utils import safe_generate
# Force load env variables
load_dotenv()

class IntegrationArchitect:
    def __init__(self):
        # Explicitly get key and configure
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found! "
                "Check your .env file."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.gemini_model)
        self.prompt_template = self._load_prompt()
        logger.info("✅ Gemini architect configured successfully")

    def _load_prompt(self) -> str:
        prompt_path = Path(config.prompts_dir) / "architecture_prompt.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Architecture prompt not found at {prompt_path}"
            )
        return prompt_path.read_text()

    def _format_case_study(self, case_study: dict) -> str:
        if not case_study:
            return "No similar case study found."
        return f"""
Project: {case_study.get('title', 'N/A')}
Industry: {case_study.get('industry', 'N/A')}
Pain Points Solved: {', '.join(case_study.get('pain_points', []))}
Architecture Pattern: {case_study.get('architecture_pattern', 'N/A')}
Solution: {case_study.get('solution_summary', 'N/A')}
Technologies Used: {', '.join(case_study.get('technologies_used', []))}
Outcomes Achieved: {', '.join(case_study.get('outcomes', []))}
Timeline: {case_study.get('timeline', 'N/A')}
Similarity Score: {case_study.get('similarity_score', 0):.2%}
        """.strip()

    def design(self, extracted_data: dict, case_studies: list) -> str:
        logger.info("🏗️  Generating architecture design with Gemini...")

        top_case_study = case_studies[0] if case_studies else {}
        case_study_text = self._format_case_study(top_case_study)
        extracted_text = json.dumps(extracted_data, indent=2)

        prompt = self.prompt_template\
            .replace("{extracted_data}", extracted_text)\
            .replace("{case_study}", case_study_text)

        response = self.model.generate_content(prompt)
        architecture_md = safe_generate(self.model, prompt)

        logger.success("✅ Architecture design complete!")
        return architecture_md