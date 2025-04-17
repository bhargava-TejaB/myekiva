import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_content(content: str) -> dict:
    """
    Parses the OpenAI response formatted in Markdown into structured sections.
    Looks for headings like ## Advanced, ## Medium, ## Basic
    """
    pattern = r"##\s*(Advanced|Medium|Basic)\s*\n(.*?)(?=\n##\s*(Advanced|Medium|Basic)|\Z)"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    parsed = {}
    for match in matches:
        level = match[0].lower()
        text = match[1].strip()
        parsed[level] = text

    return parsed


def generate_education_content(topic: str) -> dict:
    """
    Generates 3-level educational content using OpenAI's GPT model.
    """
    prompt = f"""
    Create educational content for the topic: "{topic}".
    Divide it into three sections:
    1. Advanced: Include basics, advancements, and future implementations.
    2. Medium: Moderate depth for average students.
    3. Basic: Simple and easy for dull students.

    Format clearly under these headers:
    - Advanced
    - Medium
    - Basic
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        return {
            "raw": content,
            "parsed": parse_content(content)
        }

    except Exception as e:
        return {"error": str(e)}
