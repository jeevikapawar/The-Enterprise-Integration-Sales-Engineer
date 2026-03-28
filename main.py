# main.py

import argparse
import sys
from pathlib import Path
from loguru import logger
from config import config


def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level=config.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
    )
    # Create logs folder if it doesnt exist
    Path("logs").mkdir(exist_ok=True)
    logger.add(
        "logs/agent.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="EAI Systems — Enterprise Integration Sales Engineer Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --transcript transcripts/example_transcript.txt
  python main.py --transcript transcripts/example_transcript.txt --verbose
  python main.py --index-only
        """
    )
    parser.add_argument(
        "--transcript", "-t",
        type=str,
        help="Path to the meeting transcript .txt file"
    )
    parser.add_argument(
        "--index-only",
        action="store_true",
        help="Only re-index case studies, dont run the agent"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Enable debug logging if verbose flag is set
    if args.verbose:
        import os
        os.environ["LOG_LEVEL"] = "DEBUG"

    # Setup logging
    setup_logging()

    # ── Index only mode ──────────────────────────────────────────────────
    if args.index_only:
        logger.info("Running in index-only mode...")
        from rag.embedder import CaseStudyEmbedder
        embedder = CaseStudyEmbedder()
        embedder.build_index()
        logger.success("Indexing complete!")
        return

    # ── Validate transcript argument ─────────────────────────────────────
    if not args.transcript:
        logger.error("Please provide a transcript file with --transcript <path>")
        logger.info(
            "Example: python main.py "
            "--transcript transcripts/example_transcript.txt"
        )
        sys.exit(1)

    if not Path(args.transcript).exists():
        logger.error(f"Transcript file not found: {args.transcript}")
        sys.exit(1)

    # ── Run the agent ────────────────────────────────────────────────────
    from agent.orchestrator import SalesEngineerAgent

    agent = SalesEngineerAgent()
    output_path = agent.run(transcript_path=args.transcript)

    logger.success(f"Done! Document saved to: {output_path}")


if __name__ == "__main__":
    main()