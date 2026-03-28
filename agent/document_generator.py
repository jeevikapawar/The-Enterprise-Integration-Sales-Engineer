# agent/document_generator.py
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
from config import config


class DocumentGenerator:
    def __init__(self):
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        extracted_data: dict,
        architecture_md: str,
        case_studies: list[dict],
        transcript_filename: str = "meeting"
    ) -> str:
        logger.info("📝 Generating Solution Design Document...")

        client_name = extracted_data.get("client_info", {}).get(
            "company_name", "Unknown_Client"
        )
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_name = client_name.replace(" ", "_").replace("/", "_")
        filename = f"solution_design_{safe_name}_{date_str}.md"
        output_path = self.output_dir / filename

        document = self._build_document(
            extracted_data, architecture_md, case_studies, date_str
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(document)

        logger.success(f"✅ Document saved to: {output_path}")
        return str(output_path)

    def _build_document(
        self,
        extracted: dict,
        architecture_md: str,
        case_studies: list[dict],
        date_str: str
    ) -> str:

        client = extracted.get("client_info", {})
        pain_points = extracted.get("pain_points", [])
        tech_stack = extracted.get("current_tech_stack", [])
        outcomes = extracted.get("desired_outcomes", [])

        doc = f"""# Solution Design Document
---
**Client:** {client.get('company_name', 'N/A')}
**Industry:** {client.get('industry', 'N/A')}
**Prepared By:** EAI Systems — Enterprise Integration Team
**Date:** {date_str}
**Status:** Draft — Pending Client Review

---

## 1. Executive Summary

This document outlines a proposed integration architecture for
**{client.get('company_name', 'the client')}**, based on the discovery
call conducted on {date_str}. The recommendations are informed by EAI Systems
experience with similar enterprise integration projects.

---

## 2. Identified Pain Points

| # | Pain Point | Description | Severity |
|---|-----------|-------------|----------|
"""
        for i, pp in enumerate(pain_points, 1):
            severity_emoji = {
                "high": "🔴", "medium": "🟡", "low": "🟢"
            }.get(pp.get("severity", "medium"), "⚪")
            doc += (
                f"| {i} | **{pp.get('title', 'N/A')}** "
                f"| {pp.get('description', 'N/A')} "
                f"| {severity_emoji} {pp.get('severity', 'N/A').capitalize()} |\n"
            )

        doc += """
---

## 3. Current Technology Stack

| Tool / Platform | Category | Notes |
|----------------|----------|-------|
"""
        for tech in tech_stack:
            doc += (
                f"| {tech.get('name', 'N/A')} "
                f"| {tech.get('category', 'N/A')} "
                f"| {tech.get('notes', '—')} |\n"
            )

        doc += """
---

## 4. Desired Outcomes & Success Criteria

| Priority | Goal | Success Metric |
|----------|------|----------------|
"""
        for outcome in outcomes:
            priority_emoji = {
                "high": "🔴", "medium": "🟡", "low": "🟢"
            }.get(outcome.get("priority", "medium"), "⚪")
            doc += (
                f"| {priority_emoji} {outcome.get('priority', 'N/A').capitalize()} "
                f"| {outcome.get('goal', 'N/A')} "
                f"| {outcome.get('metric', 'TBD')} |\n"
            )

        doc += f"""
---

## 5. Constraints & Requirements

- **Timeline:** {extracted.get('timeline', 'Not specified')}
- **Budget Range:** {extracted.get('budget_range', 'Not specified')}
- **Additional Notes:** {extracted.get('additional_notes', 'None')}

---

## 6. Proposed Architecture & Solution Design

{architecture_md}

---

## 7. Similar Case Study Reference

"""
        if case_studies:
            top = case_studies[0]
            doc += f"""### Most Relevant Past Project: {top.get('title', 'N/A')}

| Field | Details |
|-------|---------|
| **Industry** | {top.get('industry', 'N/A')} |
| **Architecture Pattern** | {top.get('architecture_pattern', 'N/A')} |
| **Timeline** | {top.get('timeline', 'N/A')} |
| **Similarity Match** | {top.get('similarity_score', 0):.0%} |

**Key Outcomes Achieved:**
"""
            for outcome in top.get("outcomes", []):
                doc += f"- ✅ {outcome}\n"

            doc += f"""
**Technologies Applied:**
{', '.join(top.get('technologies_used', []))}

**Solution Approach:**
{top.get('solution_summary', 'N/A')}
"""
            if len(case_studies) > 1:
                doc += "\n### Additional Related Projects\n\n"
                for study in case_studies[1:]:
                    doc += (
                        f"- **{study.get('title')}** "
                        f"({study.get('industry')}) — "
                        f"{study.get('similarity_score', 0):.0%} match\n"
                    )

        doc += f"""
---

## 8. Recommended Next Steps

| Step | Action | Owner | Timeline |
|------|--------|-------|----------|
| 1 | Review and approve Solution Design Document | Client | 3-5 business days |
| 2 | Technical deep-dive call with IT team | EAI Systems + Client | Week 2 |
| 3 | Finalize tooling and licensing | EAI Systems | Week 2-3 |
| 4 | Kick off Phase 1 implementation | EAI Systems | Week 4 |
| 5 | Phase 1 review checkpoint | Both parties | Day 30 |

---

*This document was auto-generated by the EAI Systems Sales Engineer Agent.*
*For questions, contact your EAI Systems account representative.*
"""
        return doc