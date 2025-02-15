import streamlit as st
from core.database import Database
from utils.helpers import format_shareable_link, generate_temp_poster
from typing import Dict
import traceback
import logging

logging.basicConfig(level=logging.INFO)


def recipient_flow(story_id: str):
    try:
        _initialize_session_state()
        story_data = _get_story_data(story_id)
        
        if story_data:
            _display_story_header(story_data)
            _handle_quiz_flow(story_data)
            
    except Exception as e:
        _handle_error(e)

def _initialize_session_state():
    """Initialize session state variables"""
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
        st.session_state.user_answers = []
        st.session_state.correct_answers = []

def _get_story_data(story_id: str) -> Dict:
    """Retrieve story data from database"""
    try:
        db = Database()
        story_data = db.get_story(story_id)
        
        if not story_data:
            st.error("📭 Story not found! Please check the link and try again.")
            return None
            
        return story_data
        
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        st.error("📚 We're having trouble accessing this story. Please try again later.")
        return None

def _display_story_header(story_data: Dict):
    """Display story title and header"""
    st.title(story_data["content"]["title"])
    st.subheader("A Romantic Comedy About Your ❤️ Story")
    st.markdown("---")

def _handle_quiz_flow(story_data: Dict):
    """Handle the quiz flow and results display"""
    if not st.session_state.quiz_submitted:
        _display_quiz(story_data)
    else:
        _display_results(story_data)

def _display_quiz(story_data: Dict):
    """Display quiz questions and collect answers"""
    try:
        for i, scene in enumerate(story_data["content"]["scenes"]):
            _display_scene(i, scene)
            
        if st.button("🎬 Submit Answers"):
            st.session_state.quiz_submitted = True
            st.rerun()
            
    except Exception as e:
        _handle_error(e)
        st.session_state.quiz_submitted = False
        st.rerun()

def _display_scene(index: int, scene: Dict):
    """Display individual scene and quiz"""
    st.markdown(f"## Scene {index + 1}")
    st.write(scene["content"])
    
    if index >= len(st.session_state.correct_answers):
        st.session_state.correct_answers.append(scene["quiz"]["correct_index"])
    
    answer = st.radio(
        scene["quiz"]["question"],
        options=scene["quiz"]["options"],
        key=f"quiz_{index}"
    )
    
    if index >= len(st.session_state.user_answers):
        st.session_state.user_answers.append(answer)
    else:
        st.session_state.user_answers[index] = answer
    
    st.caption(f"**Director's Note:** {scene['commentary']}")
    st.markdown("---")

def _display_results(story_data: Dict):
    """Display quiz results and bloopers"""
    try:
        with st.spinner("🎥 Generating your results..."):
            score = _calculate_score(story_data)
            poster_path = generate_temp_poster(score, story_data["content"]["title"])
        
        st.subheader("🎉 Results")
        st.image(poster_path)
        st.markdown(f"### Your Score: {score}/{len(story_data['content']['scenes'])}")
        
        if score < len(story_data["content"]["scenes"]):
            _display_bloopers(story_data, score)
            
    except Exception as e:
        _handle_error(e)
        st.error("We're having trouble generating your results. Please try again.")
        st.session_state.quiz_submitted = False
        st.rerun()

def _calculate_score(story_data: Dict) -> int:
    """Calculate user's score"""
    return sum(
        1 for u, c, scene in zip(
            st.session_state.user_answers, 
            st.session_state.correct_answers, 
            story_data["content"]["scenes"]
        ) if u == scene["quiz"]["options"][c]
    )

def _display_bloopers(story_data: Dict, score: int):
    """Display bloopers for incorrect answers"""
    st.subheader("🎬 Blooper Reel")
    for i, (u, c) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers)):
        scene = story_data["content"]["scenes"][i]
        if u != scene["quiz"]["options"][c]:
            if "bloopers" in story_data["content"] and i < len(story_data["content"]["bloopers"]):
                blooper = story_data["content"]["bloopers"][i]
                st.write(f"🎬 Scene {i+1}: {blooper}")
            else:
                st.write(f"🎬 Scene {i+1}: No blooper available")
    st.markdown("---")

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