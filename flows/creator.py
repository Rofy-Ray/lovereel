import os
import streamlit as st
from core.database import Database
from core.ai_client import DeepSeekClient
from models.schemas import StoryCreate, Memory, QAPair
from utils.helpers import format_shareable_link
import logging

logging.basicConfig(level=logging.INFO)



STORY_PROMPT = """Generate a romantic comedy story containing exactly 3 scenes using these real memories:
{memories}

And these personal facts about me:
{personal_facts}

Format as valid JSON according to the specified schema.

USE the QUIZ, OPTIONS, or CORRECT_INDEX (ANSWERS) as needed to generate the content but DO NOT show them in the generated content EXCEPT for the actual QUIZ and OPTIONS.
"""

# def creator_flow():
#     st.title("Create Your ❤️ Story Quiz")
    
#     if 'current_step' not in st.session_state:
#         st.session_state.current_step = 0
#         st.session_state.story_data = {"memories": [], "personal_qa": []}

#     if st.session_state.current_step == 0:
#         st.subheader("Share 3 Key Memories")
#         memory_data = []
        
#         for i in range(3):
#             title = st.text_input(
#                 f"Memory {i+1} Title", 
#                 key=f"memory_title_{i}",
#                 value=st.session_state.story_data["memories"][i]["title"] 
#                     if len(st.session_state.story_data["memories"]) > i 
#                     else ""
#             )
#             description = st.text_area(
#                 f"Memory {i+1} Description", 
#                 key=f"memory_desc_{i}",
#                 value=st.session_state.story_data["memories"][i]["description"] 
#                     if len(st.session_state.story_data["memories"]) > i 
#                     else ""
#             )
#             memory_data.append({"title": title, "description": description})
        
#         if st.button("Next"):
#             if all(m["title"] and m["description"] for m in memory_data):
#                 st.session_state.story_data["memories"] = memory_data
#                 st.session_state.current_step = 1
#             else:
#                 st.error("Please fill all memory fields!")

#     elif st.session_state.current_step == 1:
#         st.subheader("Answer 3 Personal Questions")
#         qa_data = []
        
#         for i in range(3):
#             question = st.text_input(
#                 f"Question {i+1}", 
#                 key=f"question_{i}",
#                 value=st.session_state.story_data["personal_qa"][i]["question"] 
#                     if len(st.session_state.story_data["personal_qa"]) > i 
#                     else ""
#             )
#             answer = st.text_input(
#                 f"Answer {i+1}", 
#                 key=f"answer_{i}",
#                 value=st.session_state.story_data["personal_qa"][i]["answer"] 
#                     if len(st.session_state.story_data["personal_qa"]) > i 
#                     else ""
#             )
#             qa_data.append({"question": question, "answer": answer})
        
#         if st.button("Generate Story"):
#             try:
#                 memories = [
#                     Memory(**m) for m in st.session_state.story_data["memories"]
#                 ]
#                 personal_qa = [
#                     QAPair(**qa) for qa in qa_data  
#                 ]
                
#                 story_data = StoryCreate(memories=memories, personal_qa=personal_qa)
#                 generate_content(story_data)
                
#             except KeyError as e:
#                 st.error(f"Missing data: {str(e)}. Please go back and fill all fields.")
#                 st.session_state.current_step = 0

# def generate_content(story_data: StoryCreate):
#     with st.spinner("Creating your romantic comedy..."):
#         prompt = STORY_PROMPT.format(
#             memories="\n".join([m.description for m in story_data.memories]),
#             personal_facts="\n".join([qa.answer for qa in story_data.personal_qa])
#         )
        
#         ai_client = DeepSeekClient()
#         db = Database()
        
#         generated_content = ai_client.generate_story_content(prompt)
#         story_id = db.save_story(story_data, generated_content)
        
#         st.session_state.generated_story_id = story_id
#         link = format_shareable_link(story_id)
#         st.success("Story created! Share this link with your loved one:")
#         st.code(link)
        
        
def creator_flow():
    try:
        st.title("Create Your ❤️ Story Quiz")
        
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
            st.session_state.story_data = {"memories": [], "personal_qa": []}

        if st.session_state.current_step == 0:
            _handle_memory_step()
        elif st.session_state.current_step == 1:
            _handle_question_step()
            
    except Exception as e:
        _handle_error(e)

def _handle_memory_step():
    """Handle memory collection step"""
    st.subheader("Share 3 Key Memories")
    memory_data = []
    
    for i in range(3):
        title = st.text_input(
            f"Memory {i+1} Title", 
            key=f"memory_title_{i}",
            value=st.session_state.story_data["memories"][i]["title"] 
                if len(st.session_state.story_data["memories"]) > i 
                else ""
        )
        description = st.text_area(
            f"Memory {i+1} Description", 
            key=f"memory_desc_{i}",
            value=st.session_state.story_data["memories"][i]["description"] 
                if len(st.session_state.story_data["memories"]) > i 
                else ""
        )
        memory_data.append({"title": title, "description": description})
    
    if st.button("Next"):
        if all(m["title"] and m["description"] for m in memory_data):
            st.session_state.story_data["memories"] = memory_data
            st.session_state.current_step = 1
            st.rerun()
        else:
            st.error("Please fill all memory fields before proceeding!")

def _handle_question_step():
    """Handle question answering step"""
    st.subheader("Answer 3 Personal Questions")
    qa_data = []
    
    for i in range(3):
        question = st.text_input(
            f"Question {i+1}", 
            key=f"question_{i}",
            value=st.session_state.story_data["personal_qa"][i]["question"] 
                if len(st.session_state.story_data["personal_qa"]) > i 
                else ""
        )
        answer = st.text_input(
            f"Answer {i+1}", 
            key=f"answer_{i}",
            value=st.session_state.story_data["personal_qa"][i]["answer"] 
                if len(st.session_state.story_data["personal_qa"]) > i 
                else ""
        )
        qa_data.append({"question": question, "answer": answer})
    
    if st.button("Generate Story"):
        try:
            memories = [
                Memory(**m) for m in st.session_state.story_data["memories"]
            ]
            personal_qa = [
                QAPair(**qa) for qa in qa_data  
            ]
            
            story_data = StoryCreate(memories=memories, personal_qa=personal_qa)
            _generate_content(story_data)
            
        except Exception as e:
            _handle_error(e)
            st.session_state.current_step = 0
            st.rerun()

def _generate_content(story_data: StoryCreate):
    """Handle story generation process"""
    try:
        with st.spinner("Creating your romantic comedy..."):
            prompt = STORY_PROMPT.format(
                memories="\n".join([m.description for m in story_data.memories]),
                personal_facts="\n".join([qa.answer for qa in story_data.personal_qa])
            )
            
            ai_client = DeepSeekClient()
            db = Database()
            
            generated_content = ai_client.generate_story_content(prompt)
            story_id = db.save_story(story_data, generated_content)
            
            st.session_state.generated_story_id = story_id
            link = format_shareable_link(story_id)
            st.success("✨ Story created! Share this link with your loved one:")
            st.code(link)
            
    except Exception as e:
        _handle_error(e)
        st.error("We encountered an issue creating your story. Please try again.")
        st.session_state.current_step = 0
        st.rerun()

def _handle_error(error: Exception) -> None:
    """Log errors while showing user-friendly message"""
    logging.error(f"Error: {str(error)}")
    logging.error(traceback.format_exc())
    
    st.error("""
    🛑 Oops! Something went wrong.
    Our team has been notified and we're working on it.
    Please try again in a moment.
    """)
    
    if st.button("🔄 Refresh and Try Again"):
        st.session_state.clear()
        st.rerun()