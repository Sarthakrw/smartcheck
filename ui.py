import streamlit as st
import pandas as pd
<<<<<<< HEAD
import random
=======
>>>>>>> f3dd055ed2e0a72a77508630f0eacdc0cb0b508b
from pdf2image import convert_from_bytes
from final_main import process_pdf, extract_diagrams, process_and_extract_key_points, combine_data

# Set page width and app title
st.set_page_config(page_title="SmartCheck", page_icon=":memo:", layout="wide")

# Function to process and combine data (cached)
@st.cache_data
def process_and_combine_data(_pages):
    processed_images = process_pdf(input_pdf=_pages, model_path='model2/train-2/weights/best.pt')
    extracted_diagrams = extract_diagrams(processed_images, model_path="model/train/weights/best.pt")
    extracted_key_points = process_and_extract_key_points(processed_images)
    combined_data = combine_data(processed_images, extracted_diagrams, extracted_key_points)
    return combined_data

# Function to display processed images
def display_processed_images(processed_images, question_index):
<<<<<<< HEAD
    st.subheader(f"Question {question_index}")
    exp = st.expander("Show Answer Image")
=======
    st.write(f"##### Question {question_index} - Processed Images:")
    exp = st.expander("Show answersheet")
>>>>>>> f3dd055ed2e0a72a77508630f0eacdc0cb0b508b
    for processed_image_data in processed_images:
        if processed_image_data['question_index'] == question_index:
            exp.image(processed_image_data['image'], caption=f"{processed_image_data['image_type']}")

# Function to display extracted diagrams
def display_extracted_diagrams(extracted_diagrams, question_index):
    for diagram_data in extracted_diagrams:
        if 'diagram_image' in diagram_data and diagram_data['question_index'] == question_index:
<<<<<<< HEAD
            st.write("#### Extracted Diagrams:")
=======
            st.write(f"##### Question {question_index} - Extracted Diagrams:")
>>>>>>> f3dd055ed2e0a72a77508630f0eacdc0cb0b508b
            st.image(diagram_data['diagram_image'], caption=f"{diagram_data['image_type']}")

# Function to display extracted key points
def display_extracted_key_points(extracted_key_points, question_index):
    st.write("##### Extracted Key Points:")
    for key_points_data in extracted_key_points:
        if 'key_points' in key_points_data and key_points_data['question_index'] == question_index:
            st.write(key_points_data['key_points'])

# Function to display final result table
def display_final_result_table(final_result_df):
    st.subheader("Final Result Table:")
    st.table(final_result_df)

# Main function
def main():
    # Streamlit UI
<<<<<<< HEAD
    st.title("SmartCheck :memo:")
=======
    st.title("SmartCheck")
    uploaded_file = st.sidebar.file_uploader("Input Student Answersheet", type=["pdf"])

>>>>>>> f3dd055ed2e0a72a77508630f0eacdc0cb0b508b

    # Sidebar menu
    with st.sidebar:
        st.sidebar.header("Home")
        uploaded_file = st.sidebar.file_uploader("Upload Answersheet", type=["pdf"])

    st.write("---")
    
    if uploaded_file is not None:
        # Convert UploadedFile to bytes
        pdf_bytes = uploaded_file.read()
        pages = convert_from_bytes(pdf_bytes, dpi=300)

        # Use cached function result
        combined_data = process_and_combine_data(pages)

        # Display options to select a question
<<<<<<< HEAD
        with st.sidebar:
            st.sidebar.header("Select a question:")
            question_index = st.sidebar.radio("Q. No.", list(combined_data.keys()))


        # Create a DataFrame for the table
        table_data = pd.DataFrame({
            "Question Number": list(combined_data.keys()),
            "Marks": [random.randint(3, 15) for _ in range(len(combined_data))]
=======
        question_index = st.sidebar.radio("Q. No.", list(combined_data.keys()))

        question_numbers = [f"Q{i}" for i in range(1, 7)]
        marks = [10, 7, 8.5, 12, 9, 11.5]

        # Create a DataFrame for the table
        table_data = pd.DataFrame({
            "Question Number": question_numbers,
            "Marks": marks
>>>>>>> f3dd055ed2e0a72a77508630f0eacdc0cb0b508b
        })

        # Display the table
        if st.sidebar.button("Final Result"):
<<<<<<< HEAD
            col1, col2 = st.columns(2)
            with col1:
                st.table(table_data)
=======
            st.table(table_data)
>>>>>>> f3dd055ed2e0a72a77508630f0eacdc0cb0b508b
            question_index = None
            st.button("Submit Student Marks")

        # Display processed images, extracted diagrams, and key points for the selected question
        if question_index is not None:
            display_processed_images(combined_data[question_index]['processed_images'], question_index)
            c1, c2 = st.columns(2)
            with c1:
                display_extracted_key_points(combined_data[question_index]['extracted_key_points'], question_index)
            with c2:
                display_extracted_diagrams(combined_data[question_index]['extracted_diagrams'], question_index)

        st.write("---")

        # Show buttons at the end of the page based on Final Result button press
        if question_index is not None:
            col1, col2, col3 = st.columns([0.2, 0.33, 0.04])
    
            if col1.button("Marks") and question_index is not None:
                # Your implementation for Marks button
                pass
            if col2.button("Report Improper Diagram Extraction") and question_index is not None:
                # Your implementation for Report button
                pass
            if col3.button("Next") and question_index is not None:
                pass

        st.write("---")

        # Control the visibility of components based on the final result page
        if question_index is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text_input("Enter Marks")
            with col2:
                st.write("Report")
                st.button("Report Improper Diagram Extraction")
            with col3:
                st.write("Next Question")
                if st.button("Next"):
                    question_keys = list(combined_data.keys())
                    current_index = question_keys.index(question_index)
                    next_index = (current_index + 1) % len(question_keys)
                    question_index = question_keys[next_index]

if __name__ == "__main__":
    main()
