import streamlit as st
st.set_page_config(
        page_title="LoveReel",
        page_icon="🎬",
        menu_items=None
    )
from flows import creator, recipient
from utils.helpers import cleanup_temp_files
from flows.creator import creator_flow
from flows.recipient import recipient_flow
import threading


def inject_css():
    with open("static/css/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    inject_css()
    query_params = st.query_params.to_dict()
    
    if "story_id" in query_params:
        recipient_flow(query_params["story_id"])
    else:
        creator_flow()
        
    cleanup_thread = threading.Thread(target=cleanup_temp_files)
    cleanup_thread.daemon = True 
    cleanup_thread.start()
        

if __name__ == "__main__":
    main()