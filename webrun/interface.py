import base64
import streamlit as st
from streamlit_option_menu import option_menu
import requests
import json

def streamlit_menu():
    with st.sidebar:
            selected = option_menu(
                menu_title=None,  # required
                options=["About Us", "Home Page", "Body Calculating", "Menu Suggestion"],  # required
                icons=["info", "house", "calculator", "egg-fried"],  # optional
                default_index=0,  # optional
                styles={
                "container": {"padding": "0!important", "background-color": "#ffefd6"},
                "icon": {"color": "#0e5e6f", "font-size": "18px"},
                "nav-link": {
                    "font-size": "18px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#0e5e6f",
                    "font-family": "Candara"
                },
                "nav-link-selected": {"background-color": "#3a8891"},
                },
            )
    return selected

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def local_css(file_name):#func to read css file -> create flake
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
