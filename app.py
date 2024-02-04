import streamlit as st
import pandas as pd
import random
from pdf2image import convert_from_bytes
from functionality import process_pdf, extract_diagrams, process_and_extract_key_points, combine_data

# Set page width and app title
st.set_page_config(page_title="SmartCheck", page_icon=":memo:", layout="wide")

# Function to process and combine data (cached)
@st.cache_data
def processing_answer_sheet(_pages):
    processed_images = process_pdf(images=_pages, model_path='model2/train-2/weights/best.pt')
    extracted_diagrams = extract_diagrams(processed_images, model_path="model/train/weights/best.pt")
    extracted_key_points = process_and_extract_key_points(processed_images)
    combined_data = combine_data(processed_images, extracted_diagrams, extracted_key_points)
    return combined_data

# Function to display processed images
def display_processed_images(processed_images, question_index):
    st.subheader(f"Question {question_index-1}")
    exp = st.expander("Show Answer Image")
    for processed_image_data in processed_images:
        if processed_image_data['question_index'] == question_index:
            exp.image(processed_image_data['image'], caption=f"{processed_image_data['image_type']}")

# Function to display extracted diagrams
def display_extracted_diagrams(extracted_diagrams, question_index):
    for diagram_data in extracted_diagrams:
        if 'diagram_image' in diagram_data and diagram_data['question_index'] == question_index:
            st.write("##### Extracted Diagrams / Tables / Letters :")
            st.image(diagram_data['diagram_image'], caption=f"{diagram_data['image_type']}")

# Function to display extracted key points
def display_extracted_key_points(extracted_key_points, question_index):
    st.write("##### Extracted Key Points:")
    for key_points_data in extracted_key_points:
        if 'key_points' in key_points_data and key_points_data['question_index'] == question_index:
            st.write(key_points_data['key_points'])

# Main function
def main():
    # Streamlit UI
    st.title("SmartCheck :memo:")

    # Sidebar menu
    with st.sidebar:
        st.sidebar.header("Home")
        uploaded_file = st.sidebar.file_uploader("Upload Answersheet", type=["pdf"])

    st.write("---")
    
    # Check if a new file is uploaded
    session_state = st.session_state
    if getattr(session_state, 'current_file', None) != uploaded_file:
        # File has changed, trigger cache clear
        st.cache_data.clear()
        # Update the current file in the session state
        session_state.current_file = uploaded_file

    if uploaded_file is not None:
        # Convert UploadedFile to bytes
        pdf_bytes = uploaded_file.read()
        pages = convert_from_bytes(pdf_bytes, dpi=300)

        # Use cached function result
        combined_data = processing_answer_sheet(pages)

        # Display options to select a question
        with st.sidebar:
            st.sidebar.header("Select a question:")
            # Start from the first question (displaying 1 in the sidebar but using index 2 internally)
            question_index_display = st.sidebar.radio("Q. No.", list(range(1, len(combined_data))))
            question_index = question_index_display + 1  # Adjusting the internal index

        # Create a DataFrame for the table
        table_data = pd.DataFrame({
            "Question Number": list(range(1, len(combined_data) + 1)),
            "Marks Awarded": [random.randint(0, 10) for _ in range(len(combined_data))]
        })

        # Display the table
        if st.sidebar.button("Final Result"):
            col1, col2 = st.columns(2)
            with col1:
                # Center-align the entire table using Streamlit's st.table
                st.table(table_data.style.set_table_styles([{"selector": "table", "props": [("margin", "auto")]}]))
            question_index = None
            # Center-align the button
            st.markdown('<div style="text-align: center;"><button>Upload Student Marks to Database</button></div>', unsafe_allow_html=True)


        # Display processed images, extracted diagrams, and key points for the selected question
        if question_index is not None:
            display_processed_images(combined_data[question_index]['processed_images'], question_index)
            c1, c2 = st.columns(2)
            with c1:
                display_extracted_key_points(combined_data[question_index]['extracted_key_points'], question_index)
            with c2:
                display_extracted_diagrams(combined_data[question_index]['extracted_diagrams'], question_index)

        st.write("---")

        # Show buttons at the end of the page
        if question_index is not None:
            col1, col2, col3 = st.columns(3)
    
            if col1.selectbox("Marks", [0,1,2,3,4,5,6,7,8,9,10]) and question_index is not None:
                # Your implementation for Marks button
                pass
            if col2.selectbox("Report", ["None", "Improper Diagram Extraction", "Incorrect Key Points"]) and question_index is not None:
                # Your implementation for Report button
                pass
            if col3.button("Next") and question_index is not None:
                pass

if __name__ == "__main__":
    main()
    
