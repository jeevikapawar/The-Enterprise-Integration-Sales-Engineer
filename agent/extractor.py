# agent/extractor.py
import json
import re
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
import google.generativeai as genai
from config import config

# Force load env variables
load_dotenv()

class TranscriptExtractor:
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
        logger.info("✅ Gemini configured successfully")

    def _load_prompt(self) -> str:
        prompt_path = Path(config.prompts_dir) / "extraction_prompt.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Extraction prompt not found at {prompt_path}"
            )
        return prompt_path.read_text()

    def extract(self, transcript: str) -> dict:
        logger.info("🔍 Starting transcript extraction...")
        prompt = self.prompt_template.replace("{transcript}", transcript)

        response = self.model.generate_content(prompt)
        raw_output = response.text

        logger.debug(f"Raw Gemini response:\n{raw_output}")
        extracted = self._parse_json_response(raw_output)
        logger.success("✅ Extraction complete!")
        return extracted

    def _parse_json_response(self, raw: str) -> dict:
        cleaned = re.sub(r"```json\n?", "", raw)
        cleaned = re.sub(r"```\n?", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Gemini returned invalid JSON: {e}")

    def pretty_print(self, extracted: dict) -> None:
        from rich.console import Console
        console = Console()

        console.print(
            "\n[bold cyan]═══ EXTRACTED CLIENT DATA ═══[/bold cyan]\n"
        )

        info = extracted.get("client_info", {})
        console.print(
            f"[bold]Company:[/bold] {info.get('company_name', 'N/A')}"
        )
        console.print(
            f"[bold]Industry:[/bold] {info.get('industry', 'N/A')}"
        )
        console.print(
            f"[bold]Team Size:[/bold] {info.get('team_size', 'N/A')}\n"
        )

        console.print("[bold red]🔴 Pain Points:[/bold red]")
        for pp in extracted.get("pain_points", []):
            console.print(
                f"  • [{pp.get('severity','?').upper()}] "
                f"{pp.get('title')}: {pp.get('description')}"
            )

        console.print("\n[bold blue]🔧 Current Tech Stack:[/bold blue]")
        for tech in extracted.get("current_tech_stack", []):
            console.print(
                f"  • {tech.get('name')} ({tech.get('category')})"
            )

        console.print("\n[bold green]🎯 Desired Outcomes:[/bold green]")
        for outcome in extracted.get("desired_outcomes", []):
            console.print(
                f"  • [{outcome.get('priority','?').upper()}] "
                f"{outcome.get('goal')}"
            )

        console.print(
            f"\n[bold]Timeline:[/bold] {extracted.get('timeline', 'N/A')}"
        )
        console.print(
            f"[bold]Budget:[/bold] {extracted.get('budget_range', 'N/A')}\n"
        )