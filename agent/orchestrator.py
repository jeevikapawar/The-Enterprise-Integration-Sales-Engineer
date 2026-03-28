# agent/orchestrator.py
import os
from loguru import logger
from rich.console import Console
from rich.panel import Panel

from agent.extractor import TranscriptExtractor
from agent.architect import IntegrationArchitect
from agent.document_generator import DocumentGenerator
from rag.retriever import CaseStudyRetriever

console = Console()


class SalesEngineerAgent:
    def __init__(self):
        logger.info("🤖 Initializing Sales Engineer Agent...")
        self.extractor = TranscriptExtractor()
        self.retriever = CaseStudyRetriever()
        self.architect = IntegrationArchitect()
        self.doc_generator = DocumentGenerator()
        logger.success("✅ Agent ready!")

    def run(self, transcript_path: str) -> str:
        console.print(Panel.fit(
            "[bold cyan]🤖 EAI Systems — Sales Engineer Agent[/bold cyan]\n"
            "[dim]Enterprise Integration Solution Design Automation[/dim]",
            border_style="cyan"
        ))

        # Step 1: Load transcript
        console.print("\n[bold]Step 1/4:[/bold] Loading transcript...")
        transcript = self._load_transcript(transcript_path)
        console.print(
            f"[green]✓[/green] Loaded "
            f"({len(transcript)} characters)"
        )

        # Step 2: Extract data
        console.print("\n[bold]Step 2/4:[/bold] Extracting client data with Claude...")
        extracted_data = self.extractor.extract(transcript)
        self.extractor.pretty_print(extracted_data)

        # Step 3: RAG retrieval
        console.print("\n[bold]Step 3/4:[/bold] Searching for similar case studies...")
        case_studies = self.retriever.retrieve(extracted_data, top_k=3)

        if case_studies:
            console.print(
                f"[green]✓[/green] Top match: "
                f"[bold]{case_studies[0].get('title')}[/bold] "
                f"({case_studies[0].get('similarity_score', 0):.0%} similarity)"
            )

        # Step 4: Architecture design
        console.print("\n[bold]Step 4/4:[/bold] Designing integration architecture...")
        architecture_md = self.architect.design(extracted_data, case_studies)
        console.print("[green]✓[/green] Architecture proposal generated")

        # Step 5: Generate document
        console.print("\n[bold]Finalizing:[/bold] Building Solution Design Document...")
        doc_path = self.doc_generator.generate(
            extracted_data=extracted_data,
            architecture_md=architecture_md,
            case_studies=case_studies,
            transcript_filename=os.path.basename(transcript_path)
        )

        console.print(Panel.fit(
            f"[bold green]✅ Document Generated![/bold green]\n\n"
            f"[dim]Saved to:[/dim] [bold]{doc_path}[/bold]",
            border_style="green"
        ))

        return doc_path

    def _load_transcript(self, path: str) -> str:
        from pathlib import Path
        transcript_path = Path(path)
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {path}")
        return transcript_path.read_text(encoding="utf-8")