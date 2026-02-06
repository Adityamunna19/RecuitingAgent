from langchain.tools import tool

@tool
def analyze_resume_tool(resume_text: str, job_description: str) -> str:
    """
    Analyze a resume against a job description and return JSON
    with score and shortlist decision.
    """

    from langchain_openai import AzureChatOpenAI
    from langchain_core.prompts import PromptTemplate
    from config.azure_config import (
        AZURE_OPENAI_API_KEY,
        AZURE_OPENAI_ENDPOINT,
        AZURE_OPENAI_API_VERSION,
        AZURE_OPENAI_DEPLOYMENT_NAME,
    )

    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        temperature=0,
    )

    prompt = PromptTemplate.from_template("""
You are a recruitment analysis agent.

Analyze the resume against the job description.
Return ONLY valid JSON with:
- candidate_name
- skills
- experience_years
- score (0-100)
- verdict (Shortlist or Reject)

Resume:
{resume}

Job Description:
{jd}
""")

    return llm.invoke(
        prompt.format(resume=resume_text, jd=job_description)
    ).content
