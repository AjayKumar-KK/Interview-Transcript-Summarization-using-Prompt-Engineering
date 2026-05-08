"""
Streamlit UI for the Interview Transcript Summarizer.

Run with:
    streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv

from summarizer import summarize

load_dotenv()

st.set_page_config(
    page_title="Interview Transcript Summarizer",
    page_icon="📝",
    layout="centered",
)

st.title("📝 Interview Transcript Summarizer")
st.caption(
    "Upload a `.txt` interview transcript. The app calls Gemini with a structured "
    "prompt and returns Topics Covered, Profile, and a Candidate Summary."
)

with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
        "Gemini model",
        options=["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
        index=0,
        help="2.5-flash is the recommended free-tier default.",
    )
    st.markdown(
        "API key is read from the `GEMINI_API_KEY` environment variable "
        "(or a `.env` file in this folder)."
    )

uploaded = st.file_uploader(
    "Upload transcript (.txt)",
    type=["txt"],
    help="Plain-text interview transcript. The two assignment samples work out of the box.",
)

if uploaded is not None:
    try:
        transcript = uploaded.read().decode("utf-8").strip()
    except UnicodeDecodeError:
        st.error("Could not decode the file as UTF-8. Please upload a plain-text `.txt` file.")
        st.stop()

    if not transcript:
        st.error("The uploaded file is empty.")
        st.stop()

    with st.expander("Preview transcript", expanded=False):
        st.text(transcript[:2000] + ("\n\n[...truncated for preview]" if len(transcript) > 2000 else ""))

    if st.button("Summarize", type="primary"):
        with st.spinner(f"Calling {model}..."):
            try:
                summary = summarize(transcript, model=model)
            except SystemExit as e:
                # summarize() calls sys.exit() on missing API key — surface that cleanly in the UI.
                st.error(str(e))
                st.stop()
            except Exception as e:
                st.error(f"API call failed: {e}")
                st.stop()

        st.success("Done.")
        st.markdown("---")
        st.markdown(summary)

        st.download_button(
            label="Download summary (.md)",
            data=summary,
            file_name=f"summary_{uploaded.name.rsplit('.', 1)[0]}.md",
            mime="text/markdown",
        )
else:
    st.info("Upload a `.txt` transcript above to get started.")