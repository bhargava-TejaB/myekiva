import os
import re
import openai
from dotenv import load_dotenv

# Load .env values
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_content(content):
    """
    Parses the raw OpenAI content into structured sections: advanced, medium, and basic.
    """
    sections = re.split(r'\b(Advanced|Medium|Basic):\b', content)
    parsed = {}
    for i in range(1, len(sections), 2):
        key = sections[i].lower()
        value = sections[i + 1].strip()
        parsed[key] = value
    return parsed

def generate_education_content(topic: str) -> dict:
    """
    Generates educational content using OpenAI's GPT model in 3 levels:
    - advanced
    - medium
    - basic

    :param topic: The topic to generate content for
    :return: A dictionary with parsed and raw response
    """
    prompt = f"""
    Create educational content for the topic: "{topic}".
    Divide it into three sections:
    1. Advanced: Include basics, advancements, and future implementations.
    2. Medium: Moderate depth for average students.
    3. Basic: Simple and easy for dull students.

    Format your answer clearly under three headers:
    - Advanced
    - Medium
    - Basic
    """

    try:
        response = openai.completions.create(
            model="gpt-4.5-preview",  # or the specific model you want to use
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000,
        )

        content = response['choices'][0]['text']

        return {
            "raw": content,
            "parsed": parse_content(content)
        }

    except Exception as e:
        return {"error": str(e)}


