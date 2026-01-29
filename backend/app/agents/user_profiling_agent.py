from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from backend.app.schemas.common import UserProfile
from backend.app.services.llm_provider import get_llm

# Initialize LLM with Fallback
llm = get_llm(temperature=0.7)

profiling_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert behavioral analyst helping to protect users from scams."),
    ("user", "Analyze the following message and metadata to infer the user's profile.\n\nMessage: {message}\nSource: {source}\n\nReturn the UserProfile as JSON.")
])

def profile_user(message: str, source: str) -> UserProfile:
    chain = profiling_prompt | llm.with_structured_output(UserProfile)
    return chain.invoke({"message": message, "source": source})
