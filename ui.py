import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pickle
from final_main import process_pdf, extract_diagrams, process_and_extract_key_points, combine_data
from pdf2image import convert_from_bytes
import io

@st.cache_data()
def process_and_combine_data(_pages):
    processed_images = process_pdf(input_pdf=_pages, model_path='model2/train-2/weights/best.pt')
    extracted_diagrams = extract_diagrams(processed_images, model_path="model/train/weights/best.pt")
    extracted_key_points = process_and_extract_key_points(processed_images)
    combined_data = combine_data(processed_images, extracted_diagrams, extracted_key_points)
    return combined_data

def display_processed_images(processed_images, question_index):
    st.write(f"### Question {question_index} - Processed Images:")
    for processed_image_data in processed_images:
        if processed_image_data['question_index'] == question_index:
            st.image(processed_image_data['image'], caption=f"{processed_image_data['image_type']}")

def display_extracted_diagrams(extracted_diagrams, question_index):
    st.write(f"### Question {question_index} - Extracted Diagrams:")
    for diagram_data in extracted_diagrams:
        if 'diagram_image' in diagram_data and diagram_data['question_index'] == question_index:
            st.image(diagram_data['diagram_image'], caption=f"{diagram_data['image_type']}")

def display_extracted_key_points(extracted_key_points, question_index):
    st.write(f"### Question {question_index} - Extracted Key Points:")
    for key_points_data in extracted_key_points:
        if 'key_points' in key_points_data and key_points_data['question_index'] == question_index:
            st.write(f"Key Points: {key_points_data['key_points']}")

def main():
    # Streamlit UI
    st.title("PDF Processor and Viewer")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Convert UploadedFile to bytes
        pdf_bytes = uploaded_file.read()
        pages = convert_from_bytes(pdf_bytes, dpi=300)

        # Use cached function result
        combined_data = process_and_combine_data(pages)

        # Display options to select a question
        question_index = st.selectbox("Select a question index", list(combined_data.keys()))

        # Display processed images, extracted diagrams, and key points for the selected question
        if question_index is not None:
            display_processed_images(combined_data[question_index]['processed_images'], question_index)
            display_extracted_diagrams(combined_data[question_index]['extracted_diagrams'], question_index)
            display_extracted_key_points(combined_data[question_index]['extracted_key_points'], question_index)

if __name__ == "__main__":
    main()