import streamlit as st
import os
import requests
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from PIL import Image
import io
import base64
import time
from openai import OpenAI

# Initialize OpenAI Client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Install and cache the driver
@st.experimental_singleton
def install_and_cache_driver():
    os.system('sbase install geckodriver')
    os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

install_and_cache_driver()

@st.experimental_singleton
def get_firefox_driver():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--no-sandbox")
    geckodriver_path = GeckoDriverManager().install()
    driver = webdriver.Firefox(executable_path=geckodriver_path, options=firefox_options)
    return driver

driver = get_firefox_driver()

# Function to encode image to Base64
def encode_image(image):
    # Convert image to RGB mode to remove transparency
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to scrape website content using requests
def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        return response.text
    except requests.RequestException:
        return None

# Function to capture screenshot using Selenium
def capture_screenshot(url):
    try:
        driver.set_window_size(1920, 1080)  # Set browser window size
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        screenshot = driver.get_screenshot_as_png()
        return Image.open(io.BytesIO(screenshot))
    except Exception:
        return None

# Function to send request to OpenAI for analysis and roast
def send_to_openai_api(scraped_content, base64_image, tone):
    prompt = f"""
    You are an AI assistant with three modes for roasting websites: "Mild", "Medium", and "Spicy". The mode is set to "{tone}".

    If the mode is "Mild", you will provide a gentle, good-natured roast with very mild criticism focused on poking fun in an inoffensive way.

    If the mode is "Medium", you will provide a roast with more noticeable humorous jabs and sarcastic observations, but still remaining relatively tame.

    If the mode is "Spicy", you will provide a very sassy, biting roast that doesn't hold back in mocking the website's flaws through ruthless comedic ridicule, while still avoiding anything too extreme or inappropriate.

    You will be given website content text [{scraped_content}] and a tone specification ({tone}), and you will generate a roast based on analyzing the text content while maintaining the specified {tone}.

    Additionally, you will be provided with a screenshot of the website, which you should use to further inform your roast by considering the visual design and layout.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4"
        )
        return chat_completion['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# Load custom CSS
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Hide main menu and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Streamlit app
def apply_custom_css():
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&display=swap" rel="stylesheet">
        <style>
            .main {
                background-color: #ffffff;
                font-family: 'Caveat', cursive;
                text-align: center;
            }
            .heading {
                text-align: center;
                margin: 0;
            }
            .input-box {
                font-size: 20px;
                padding: 10px;
                margin: 20px auto;
                width: 50%;
                font-family: 'Caveat', cursive;
            }
            .button {
                font-size: 20px;
                padding: 10px;
                margin: 20px auto;
                width: 50%;
                background-color: #ff5252;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-family: 'Caveat', cursive;
            }
            .button:hover {
                background-color: #e04848;
            }
            .spicy-level select {
                font-size: 20px;
                padding: 10px;
                width: 50%;
                margin: 20px auto;
                text-align: center;
                font-family: 'Caveat', cursive;
            }
            .floating-text {
                position: fixed;
                bottom: 0;
                width: 100%;
                background-color: #ffffff;
                padding: 10px 0;
                text-align: center;
                font-size: 18px;
                color: #ff5252;
                font-family: 'Caveat', cursive;
            }
        </style>
    """, unsafe_allow_html=True)

apply_custom_css()

st.markdown("""
            <h1 class='heading'><span style='color: #ff5252'>Roast</span><br><span style='color: #000000'>My Website</span></h1>
            """, unsafe_allow_html=True)

# Input for website URL
website_url = st.text_input("", placeholder="https://example.com")

# Mode selection
mode = st.selectbox("Choose your roast level:", ["Mild 🌶️", "Medium 🌶️🌶️", "Spicy 🌶️🌶️🌶️"])

# Roast button
if st.button("Get Roasted 🔥"):
    if website_url:
        try:
            with st.spinner('Scraping website...'):
                scraped_content = scrape_website(website_url)
                if not scraped_content:
                    raise Exception("Failed to scrape website")

            with st.spinner('Capturing screenshot...'):
                screenshot = capture_screenshot(website_url)
                if not screenshot:
                    raise Exception("Failed to capture screenshot")

            st.image(screenshot, caption='Screenshot of the website')

            with st.spinner('Encoding image...'):
                base64_image = encode_image(screenshot)

            with st.spinner('Using vision...'):
                vision_analysis = send_to_openai_api(scraped_content, base64_image, tone=mode.lower())
                if not vision_analysis:
                    raise Exception("Failed to analyze vision")

            st.write(vision_analysis)

        except Exception as e:
            st.error(f"Failed to roast website: {str(e)}")

    else:
        st.error("Please enter a valid website URL.")
