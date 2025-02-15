
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from models.schemas import StoryCreate, GeneratedContent
from typing import Optional, Dict

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DB_NAME')]
        self.stories = self.db["valz"]

    def save_story(self, story_data: StoryCreate, generated_content: GeneratedContent) -> str:
        doc = {
            "meta": story_data.dict(),
            "content": generated_content.dict(),
            "access_key": self._generate_access_key()
        }
        result = self.stories.insert_one(doc)
        return str(result.inserted_id)
    
    def get_story(self, story_id: str) -> Optional[Dict]:
        return self.stories.find_one({"_id": ObjectId(story_id)})

    def _generate_access_key(self) -> str:
        import secrets
        return secrets.token_urlsafe(16)    