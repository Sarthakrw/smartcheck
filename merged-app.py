##                                             import libraries
import streamlit as st
import google.generativeai as genai
from PIL import Image
from pdf2image import convert_from_bytes
from dotenv import load_dotenv
import os
import cv2
from ultralytics import YOLO
from IPython.display import Image, display





##                                  setup and load all models used ( Gemini, YOLO )

# gemini vision
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

generation_config = {
  "temperature": 0.1,
  "top_p": 0.2,
  "top_k": 20,
}
gemini_vision = genai.GenerativeModel("gemini-pro-vision", generation_config=generation_config)

# YOLO - Diagram Extractor model
diagram_extract = YOLO("model/train/weights/best.pt")

# YOLO - Ques Separator model
ques_separate = YOLO("model2/train-2/weights/best.pt")






#               All functions ( question separator, text extractor, key-points extractor, diagram extractor )





# Question separator :-
def separate_questions(image):
    # Make predictions
    results = ques_separate(image)

    processed_images = []

    # Check if there are no detections
    if len(results[0].boxes.data) == 0:
        # Save the entire image
        processed_images.append(image.copy())

    else:
        # Sort detections based on y-coordinate (top to bottom)
        detections = sorted(results[0].boxes.data, key=lambda det: det[1])

        # Save the regions between consecutive lines and from the last line to the bottom of the page
        for i in range(len(detections)):
            if i == 0:
                # Save from the top of the image to the first line
                cut_image = image[:int(detections[i][1]), :]
                processed_images.append(cut_image.copy())
            else:
                # Save from the current line to the next line or to the bottom of the page
                _, y_prev, _, _, _, _ = detections[i - 1]
                _, y_curr, _, _, _, _ = detections[i]
                cut_image = image[int(y_prev):int(y_curr), :]
                processed_images.append(cut_image.copy())

        # If there are detections, save from the last line to the bottom of the page
        _, y_last, _, _, _, _ = detections[-1]
        last_line_cut_image = image[int(y_last):, :]
        processed_images.append(last_line_cut_image.copy())

    return processed_images






# Key-Points Extractor:-
def generate_key_points(image_file):
    prompt = """You are an experienced teacher, Extract key points from the text in this image, do not add extra 
    text or content other than the text that is present in the image also do not output all the extracted test 
    as response, only mention question/answer number as in the image and main key points from the text in image:"""

    # prompt = '''Extract all the text from the image'''

    response = gemini_vision.generate_content([prompt, image_file], stream=True)
    response.resolve()

    return response.text




# Diagram Extractor:-
def extract_diagram(image):
    original_image = cv2.imread(image_path)

    # Make predictions
    results = diagram_extract(image_path)

    # Iterate over each detected object
    for det in results[0].boxes.data:
        # Get coordinates of the bounding box
        x, y, width, height, confidence, class_id = det.tolist()

        # Draw bounding box on the image
        color = (0, 255, 0)  # Green color for the bounding box
        thickness = 2
        start_point = (int(x), int(y))
        end_point = (int(x + width), int(y + height))
        original_image = cv2.rectangle(original_image, start_point, end_point, color, thickness)

    # Save the image with bounding boxes
    output_image_path = os.path.join(output_folder, filename)
    cv2.imwrite(output_image_path, original_image)







##                                              Streamlit app layout :


st.title("SmartCheck")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
st.write("---")

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    pages = convert_from_bytes(pdf_bytes, dpi=300)  # Use convert_from_bytes instead

    # Traversing over all the pages in the PDF file
    for page_num, page_image in enumerate(pages, start=1):
        # Calling question separator function
        processed_images = ques_separate(page_image)
        for i in processed_images:
            st.image(i)


        # Getting Key points for each img we got by calling "question separator"
        key_points = generate_key_points(page_image)

        # Calling diagram extractor function
        diagrams = extract_diagram()

        # Displaying key points and diagrams
        st.write(f"**Page {page_num} Key Points:**")
        st.markdown(key_points)
        st.image(diagrams)







# WORKFLOW :-

# 1. User Input Answersheet in PDF format
# 2. Converting PDF to images
# 3. Passing images to "Ques-separator" function (we receive cut-images from this function)

#                     ques_images = Ques-separator(PDF pages images)

# 4. Passing each image to "Gemini-vision" for text extraction and key-points extraction (we receive key-points in string from this function)

#                     key-points = Gemini-vision(ques_images)

# 5. Passing each image we received from "Ques-separator" function to "Diagram-extractor" function

#                     diagrams = Diagram-extractor(ques_images)

# 6. Displaying "key-points" and "diagrams" on the screen.