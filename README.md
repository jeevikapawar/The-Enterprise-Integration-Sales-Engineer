#Enterprise-Integration-Sales-Engineer
Building a Technical Sales Agent that analyzes client meeting transcripts and automatically generates Solution Design Documents by identifying pain points, tech stack, and desired outcomes—augmented with relevant case studies from a RAG system.


Overview
The Enterprise Integration Sales Engineer Agent is an AI-powered agentic system designed to automate the technical sales discovery process. By ingesting raw meeting transcripts, the agent intelligently extracts key client information, reasons over a knowledge base of past projects, and generates a professional Solution Design Document — all without manual intervention.
This tool bridges the gap between a client discovery call and a formal technical proposal, cutting down solution design time from days to minutes.


Features
1. Transcript Ingestion — Accepts raw text transcripts from 15-minute discovery calls
2. Automatic Extraction of:
- Client Pain Points
- Current Technology Stack
- Desired Outcomes & Success Criteria
3. RAG-Powered Case Study Matching — Queries EAI Systems' internal case study database to surface relevant past projects as references
4. Architectural Reasoning — Uses Claude to propose a tailored integration architecture based on extracted context
5. Automated Solution Design Document — Outputs a structured, client-ready proposal document
6. Agentic Workflow — Fully orchestrated multi-step reasoning pipeline with minimal human input


Prerequisites
Before getting started, ensure you have the following:
Python 3.10+
An Anthropic API Key (Claude access)
A Microsoft Copilot Studio account
A Gravity account with RAG pipeline access
Access to EAI Systems' internal case study library (JSON or PDF format)
pip or conda for dependency management
