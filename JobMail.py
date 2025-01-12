import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import PyPDF2 as pdf
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader

load_dotenv()

# Custom CSS styling with background color animation
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    /* Keyframe for smooth background color transition */
    @keyframes bgColorChange {
        0% { background: #df17e6; }
        25% { background: #25a0db; }
        50% { background: #7b18de; }
        75% { background: #25a0db; }
        100% { background: #df17e6; }
    }

        @keyframes waveMotion {
        0% {
            background-position: 0 0;
        }
        100% {
            background-position: 100% 0;
        }
    }

    .stApp {
        background: linear-gradient(120deg, #4e21cc 25%, #367b9c 50%, #8231d4 75%);
        background-size: 200% 100%;
        animation: waveMotion 15s ease-in-out infinite;
        font-family: 'Poppins', sans-serif;
    }


    .main-header {
        background: rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .css-1629p8f h1 {  /* Title styling */
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin-bottom: 1.5rem !important;
        background: linear-gradient(90deg, #ffffff, #e0e0e0);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2) !important;
    }

    .stTextInput > label {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        border-radius: 10px !important;
    }

    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 2rem !important;
        text-align: center !important;
    }

    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.8rem 2rem !important;
        border-radius: 25px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin-top: 1rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
    }

    .stTextArea > label {
        color: #ffffff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }

    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        font-family: 'Poppins', sans-serif !important;
    }

    .stAlert {
        background: rgba(255, 87, 87, 0.1) !important;
        border: 1px solid rgba(255, 87, 87, 0.2) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 1rem !important;
    }

    .uploadedFileName {
        color: white !important;
    }

    .css-10trblm {
        color: white !important;
        margin-top: 2rem !important;
        font-weight: 600 !important;
    }

    .stSpinner > div {
        border-color: #4CAF50 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("📋 How to Use")
st.sidebar.markdown("""
1. **🔗 Enter Job Link:**  
   Provide the link to the job description webpage.

2. **📄 Upload Resume:**  
   Upload your resume in PDF format.

3. **✨ Generate Email:**  
   Click the button to create a personalized job application email.

4. **📧 Copy & Use:**  
   Copy the email and send it to the recruiter!
""")
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tips for Best Results:**")
st.sidebar.markdown("""
- Ensure the job link is active and accurate.  
- Use a well-structured resume in PDF format.  
- Be patient while the AI processes your request.
""")

# Main app layout with styled container
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("📧 Job Application Email Generator")
st.markdown("</div>", unsafe_allow_html=True)

# Inputs: job link and resume upload
job_link = st.text_input("🔗 Enter Job Link:")
uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])


# Function to scrape job website
def scrape_website(job_link):
    if not job_link:
        return "Please provide a valid job link."

    llm_scrape = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.5,
        groq_api_key=os.getenv("GROQ_API_KEY1")
    )

    loader = WebBaseLoader(job_link)
    page_data = loader.load().pop().page_content
    prompt_job_content = PromptTemplate.from_template(
        """
           ### SCRAPED TEXT FROM WEBSITE:
           {page_data}
           ### INSTRUCTION:
           Extract the following from the scraped text:
           - Company Details (e.g., Name)
           - Job Title and Role
           - Job Description
           - Skills and Competencies
           - Qualifications and Experience
           and any other important data
        """
    )

    chain_extract = prompt_job_content | llm_scrape
    res = chain_extract.invoke(input={'page_data': page_data})
    return res.content


# Function to extract text from the resume PDF
def extract_text(uploaded_file):
    if uploaded_file is not None:
        reader = pdf.PdfReader(uploaded_file)
        pages = len(reader.pages)
        text = ""
        for page_num in range(pages):
            page = reader.pages[page_num]
            text += str(page.extract_text())
        return text
    return "No resume uploaded."


# Function to generate job application email
def generate_mail(resume_content, job_content):
    if not resume_content or not job_content:
        return "Resume or job content is missing."

    llm_mail = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.5,
        groq_api_key=os.getenv("GROQ_API_KEY2")
    )

    prompt_mail = PromptTemplate.from_template(
        """
            ### JOB CONTENT:
            {job_content}

            ### USER RESUME:
            {resume_content}

            ### INSTRUCTION:
            Create a personalized job application email using the above details. 
            Include:
            1. A formal greeting
            2. A brief introduction about the candidate
            3. Explanation of why the user is interested in the job
            4. Value proposition and how the user’s skills align with the job
            5. Call to action (interview invitation)
            6. Polite closing with contact details

            Ensure the email maintains a professional and concise tone.
        """
    )

    mail_extract = prompt_mail | llm_mail
    final_mail = mail_extract.invoke(input={'job_content': job_content, 'resume_content': resume_content})
    return final_mail.content


# Main logic to generate the job application email
if st.button("✨ Generate Job Application Email"):
    if uploaded_file and job_link:
        with st.spinner("🔄 Processing your request..."):
            resume_content = extract_text(uploaded_file)
            job_content = scrape_website(job_link)
            email = generate_mail(resume_content, job_content)

            st.markdown("### 📝 Generated Job Application Email:")
            st.text_area("Email Content", email, height=600, max_chars=None)
    else:
        st.error("⚠ Please upload a resume and provide a job link.")