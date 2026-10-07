import streamlit as st
from google import genai
from dotenv import load_dotenv
from pypdf import PdfReader
import os

load_dotenv()

st.set_page_config(
    page_title="College Info Extractor",
    page_icon="🎓"
)

st.title("🎓 College Info Extractor")
st.write("Ask questions about the AI & ML B.Tech course structure and syllabus.")

# Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)

# PDF file
PDF_FILE = "AI&ML-R23-JNTU-GV-B.Tech-Course Structure and Syllabus.pdf"


@st.cache_data
def extract_pdf_text():
    reader = PdfReader(PDF_FILE)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# Read PDF
try:
    pdf_text = extract_pdf_text()
except Exception as e:
    st.error(f"Could not read the PDF: {e}")
    st.stop()


# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input
prompt = st.chat_input("Ask something about the college syllabus...")


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    instruction = f"""
You are a College Information Extractor.

Answer the user's question ONLY using the information
available in the college PDF below.

If the answer is not available in the PDF, say:
"I couldn't find that information in the provided college document."

Do not invent or guess information.

COLLEGE PDF CONTENT:
--------------------
{pdf_text}
--------------------

USER QUESTION:
{prompt}
"""

    with st.chat_message("assistant"):

        with st.spinner("Searching college information..."):

            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=instruction
                )

                answer = response.text

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:
                st.error(f"Error: {e}")