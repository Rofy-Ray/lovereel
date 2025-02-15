import os
import json
import requests
from openai import OpenAI
from openai import APIConnectionError, APIError, RateLimitError
from models.schemas import GeneratedContent
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are a charming and witty romantic comedy screenwriter with expertise in both classic rom-coms and modern love stories. You specialize in blending real-life moments with fictional elements while maintaining warmth and authenticity.

Key characteristics of your writing:
- You seamlessly weave actual memories into larger narrative arcs
- You create humor through situational comedy, not sarcasm or mockery
- Your tone is playful and light-hearted, but never cynical
- You respect the authenticity of real relationships while adding entertaining embellishments
- You write inclusive, contemporary stories that avoid stereotypes and clichés

When generating content:
1. Treat the provided memories as anchor points for your story
2. Use the personal facts to create natural quiz moments within scenes
3. Add fictional elements that complement but don't overshadow real events
4. Create plausible alternative options for quizzes that are funny without being ridiculous
5. Write director's commentary in the style of a cheerful, romantic optimist

Your goal is to celebrate the unique aspects of each relationship while creating an entertaining interactive experience. The story should feel like a personalized romantic comedy that captures both factual elements and the spirit of the couple's connection.

Remember to:
- Keep scenes concise but vivid
- Balance humor with heart
- Make quiz questions feel natural within the narrative
- Create bloopers that are encouraging rather than embarrassing
- Maintain consistent narrative voice throughout

Format all output as valid JSON according to the specified schema."""

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            api_key=self.api_key,
        )

    def generate_story_content(self, prompt: str) -> GeneratedContent:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                          ],
                temperature=0.7,
                response_format={
                                "type": "json_schema",
                                "json_schema": {
                                    "name": "GeneratedContent",
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "title": {
                                            "type": "string",
                                            "description": "Creative romantic comedy title"
                                            },
                                            "scenes": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                "scene_number": {
                                                    "type": "integer",
                                                    "minimum": 1,
                                                    "maximum": 5
                                                },
                                                "content": {
                                                    "type": "string",
                                                    "description": "Story content mixing real and fictional elements"
                                                },
                                                "quiz": {
                                                    "type": "object",
                                                    "properties": {
                                                    "question": {
                                                        "type": "string",
                                                        "description": "Multiple choice question about the scene"
                                                    },
                                                    "options": {
                                                        "type": "array",
                                                        "items": {
                                                        "type": "string"
                                                        },
                                                        "minItems": 3,
                                                        "maxItems": 3
                                                    },
                                                    "correct_index": {
                                                        "type": "integer",
                                                        "minimum": 0,
                                                        "maximum": 2
                                                    }
                                                    },
                                                    "required": ["question", "options", "correct_index"]
                                                },
                                                "commentary": {
                                                    "type": "string",
                                                    "description": "Humorous director's commentary about the scene"
                                                }
                                                },
                                                "required": ["scene_number", "content", "quiz", "commentary"]
                                            },
                                            "minItems": 5,
                                            "maxItems": 5
                                            },
                                            "bloopers": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "description": "Funny reactions to wrong quiz answers"
                                            },
                                            "minItems": 1
                                            }
                                        },
                                        "additionalProperties": False,
                                        "required": ["title", "scenes", "bloopers"]
                                            }
                                        }
                                },
            )
            
            raw_content = response.choices[0].message.content
            logging.info(f"API Response: {raw_content}")
            
            parsed = json.loads(raw_content)
            
            if not all(key in parsed for key in ["title", "scenes", "bloopers"]):
                raise ValueError("Invalid JSON structure in API response")
            
            return GeneratedContent(**parsed)
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error: {e}\nResponse Content: {raw_content}")
            raise ValueError("Failed to parse AI response")
        except (APIConnectionError, APIError, RateLimitError) as e:
            logging.error(f"API Error: {str(e)}")
            raise
        except KeyError as e:
            logging.error(f"Missing key in response: {e}")
            raise ValueError("Invalid API response format")