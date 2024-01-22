import streamlit as st
import google.generativeai as genai
from PIL import Image
from pdf2image import convert_from_path
import pytesseract  # For handwritten text extraction
from dotenv import load_dotenv
import os

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Function to extract text from an image (including handwritten)
def extract_text_from_image(image_file):
    text = pytesseract.image_to_string(Image.open(image_file))
    return text


model = genai.GenerativeModel("gemini-pro-vision")

# Function to generate key points using Gemini Pro Vision
def generate_key_points(image_file):
    prompt = f"Extract key points from the text in this image, do not add extra lines or content other than the text that is present in the image also do not output all the extracted test as response, only mention main key points from the text in image:"
    response = model.generate_content([prompt, image_file], stream=True)
    response.resolve()

    return response.text


# Streamlit app layout
st.title("Key Points Extractor with Gemini")


uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    pages = convert_from_path(uploaded_file.name, dpi=200)  # Adjust DPI as needed

    for page_num, page_image in enumerate(pages, start=1):
        key_points = generate_key_points(page_image)
        st.write(f"**Page {page_num} Key Points:**")
        st.markdown(key_points)