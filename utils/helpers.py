import os
import random
import requests
import tempfile
import time
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

temp_dir = tempfile.mkdtemp()


def validate_memory_input(title: str, description: str) -> bool:
    """Validate memory input fields"""
    return len(title.strip()) > 2 and len(description.strip()) > 10


def generate_temp_poster(score: int, story_title: str) -> str:
    """Generate AI-powered movie poster using DeepSeek"""
    try:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        prompt = f"""Create a romantic comedy movie poster with these elements:
        - Style: Romantic comedy with vintage elements
        - Visual theme: Combine whimsical romance and playful humor
        - Color scheme: Warm pastels with gold accents
        - Required elements: Visual representations of love (hearts, roses, etc.) and comedy (playful/funny moments between couples)
        - Quality rating: Represent {score}/3 through visual star elements

        IMPORTANT: This image MUST NOT contain any text, words, letters, numbers, or written elements of any kind. The entire poster should communicate purely through visuals, symbols, and imagery.
        """
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            n=1,
            quality="standard"
        )
        
        image_url = response.data[0].url
        
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        # img_path = f"poster_{score}_{story_title[:20]}.png" 
        img_path = os.path.join(temp_dir, f"poster_{score}_{story_title[:20]}.png")
        img.save(img_path)
        return img_path
    
    except Exception as e:
        st.error(f"AI poster generation failed: {str(e)}")
        return _generate_fallback_poster(score, story_title)

def _generate_fallback_poster(score: int, title: str) -> str:
    """Local fallback poster generator"""
    img = Image.new('RGB', (1024, 1792), color=(20, 20, 20))
    d = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()

    d.text((100, 200), title, fill=(255,255,255), font=font)
    d.text((100, 300), f"Score: {score}/3", fill=(255,255,0), font=font)
    img_path = os.path.join(temp_dir, "temp_poster.png")
    img.save(img_path)
    return img_path

def format_shareable_link(story_id: str) -> str:
    """Generate formatted shareable URL"""
    base_url = os.getenv("BASE_URL", "http://localhost:8501")
    return f"{base_url}/?story_id={story_id}"

def cleanup_temp_files():
    while True:
        cutoff = time.time() - 300  
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            if os.path.getctime(filepath) < cutoff:
                os.remove(filepath)
        time.sleep(60) 