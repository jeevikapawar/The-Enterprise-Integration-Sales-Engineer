# app.py
import streamlit as st
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="EAI Systems — Sales Engineer Agent",
    page_icon="🤖",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────
st.title("🤖 EAI Systems — Enterprise Integration Agent")
st.markdown(
    "**Upload a meeting transcript and get a full "
    "Solution Design Document in seconds!**"
)
st.divider()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/artificial-intelligence.png",
        width=80
    )
    st.header("⚙️ Settings")
    st.success("✅ Gemini AI Connected")
    st.info("📚 3 Case Studies Loaded")

    st.divider()
    st.markdown("### How It Works")
    st.markdown("""
    1. 📝 Upload transcript
    2. 🧠 AI extracts data
    3. 🔍 RAG finds similar projects
    4. 🏗️ Architecture is designed
    5. 📄 Document is generated
    """)

    st.divider()
    st.markdown("Built with Gemini AI + FAISS RAG")

# ── Main Area ─────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input: Meeting Transcript")

    # Option 1: Upload file
    uploaded_file = st.file_uploader(
        "Upload a .txt transcript file",
        type=["txt"]
    )

    # Option 2: Paste text
    st.markdown("**Or paste your transcript directly:**")
    pasted_text = st.text_area(
        "Paste transcript here",
        height=300,
        placeholder="Paste your meeting transcript here..."
    )

    # Load example button
    if st.button("📋 Load Example Transcript", use_container_width=True):
        example_path = Path("transcripts/example_transcript.txt")
        if example_path.exists():
            pasted_text = example_path.read_text()
            st.session_state["transcript_text"] = pasted_text
            st.rerun()

    # Store transcript text
    if uploaded_file:
        transcript_text = uploaded_file.read().decode("utf-8")
        st.success(f"✅ File uploaded: {uploaded_file.name}")
    elif "transcript_text" in st.session_state:
        transcript_text = st.session_state["transcript_text"]
        st.text_area(
            "Loaded transcript",
            value=transcript_text,
            height=300
        )
    elif pasted_text:
        transcript_text = pasted_text
    else:
        transcript_text = None

# ── Run Button ────────────────────────────────────────────────
st.divider()
run_button = st.button(
    "🚀 Generate Solution Design Document",
    type="primary",
    use_container_width=True
)

# ── Processing ────────────────────────────────────────────────
if run_button:
    if not transcript_text:
        st.error("❌ Please upload or paste a transcript first!")
    else:
        # Save transcript to temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8"
        ) as tmp:
            tmp.write(transcript_text)
            tmp_path = tmp.name

        try:
            # ── Progress Bar ──────────────────────────────────
            progress = st.progress(0)
            status = st.status(
                "🤖 Agent is working...",
                expanded=True
            )

            with status:
                # Step 1
                st.write("📝 Step 1/4: Loading transcript...")
                progress.progress(10)

                # Step 2
                st.write("🧠 Step 2/4: Extracting client data with Gemini...")
                progress.progress(25)

                from agent.extractor import TranscriptExtractor
                extractor = TranscriptExtractor()
                extracted_data = extractor.extract(transcript_text)
                progress.progress(50)

                # Step 3
                st.write("🔍 Step 3/4: Searching similar case studies...")
                from rag.retriever import CaseStudyRetriever
                retriever = CaseStudyRetriever()
                case_studies = retriever.retrieve(extracted_data, top_k=3)
                progress.progress(70)

                # Step 4
                st.write("🏗️ Step 4/4: Designing architecture...")
                from agent.architect import IntegrationArchitect
                architect = IntegrationArchitect()
                architecture_md = architect.design(extracted_data, case_studies)
                progress.progress(85)

                # Step 5
                st.write("📄 Finalizing document...")
                from agent.document_generator import DocumentGenerator
                doc_gen = DocumentGenerator()
                doc_path = doc_gen.generate(
                    extracted_data=extracted_data,
                    architecture_md=architecture_md,
                    case_studies=case_studies
                )
                progress.progress(100)
                status.update(
                    label="✅ Document Generated!",
                    state="complete"
                )

            # ── Success ───────────────────────────────────────
            st.success("🎉 Solution Design Document Generated!")

            # ── Show Extracted Data ───────────────────────────
            with col2:
                st.header("📊 Extracted Client Data")

                client = extracted_data.get("client_info", {})

                # Client info metrics
                m1, m2, m3 = st.columns(3)
                m1.metric(
                    "Company",
                    client.get("company_name", "N/A")
                )
                m2.metric(
                    "Industry",
                    client.get("industry", "N/A")
                )
                m3.metric(
                    "Team Size",
                    client.get("team_size", "N/A")
                )

                st.divider()

                # Pain points
                st.markdown("### 🔴 Pain Points")
                for pp in extracted_data.get("pain_points", []):
                    severity = pp.get("severity", "medium")
                    color = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(severity, "⚪")
                    st.markdown(
                        f"{color} **{pp.get('title')}**: "
                        f"{pp.get('description')}"
                    )

                st.divider()

                # Tech stack
                st.markdown("### 🔧 Current Tech Stack")
                techs = extracted_data.get("current_tech_stack", [])
                tech_cols = st.columns(3)
                for i, tech in enumerate(techs):
                    tech_cols[i % 3].info(
                        f"**{tech.get('name')}**\n\n"
                        f"{tech.get('category')}"
                    )

                st.divider()

                # Case study match
                if case_studies:
                    st.markdown("### 📚 Best Case Study Match")
                    top = case_studies[0]
                    st.success(
                        f"**{top.get('title')}** — "
                        f"{top.get('similarity_score', 0):.0%} match"
                    )

            # ── Document Preview ──────────────────────────────
            st.divider()
            st.header("📄 Generated Solution Design Document")

            doc_content = Path(doc_path).read_text(encoding="utf-8")

            # Preview
            with st.expander("👁️ Preview Document", expanded=True):
                st.markdown(doc_content)

            # Download button
            st.download_button(
                label="⬇️ Download Solution Design Document",
                data=doc_content,
                file_name=Path(doc_path).name,
                mime="text/markdown",
                use_container_width=True,
                type="primary"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.code(str(e))

        finally:
            os.unlink(tmp_path)