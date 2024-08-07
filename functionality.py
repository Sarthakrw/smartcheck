import cv2
from ultralytics import YOLO
import pickle
from pdf2image import convert_from_path, convert_from_bytes
import google.generativeai as genai
from PIL import Image, PngImagePlugin
from dotenv import load_dotenv
import os
import numpy as np

# question separator 

def process_pdf(images, model_path):

    # Load the trained YOLOv8 model
    model = YOLO(model_path)

    # Initialize a list to store processed images and information
    processed_images = []

    # Initialize variables for tracking currently active question index
    current_question_index = 1

    # Iterate over each image from the PDF
    for page_number, original_image in enumerate(images, start=1):
        # Convert PIL image to OpenCV format
        original_image_cv2 = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)

        # Make predictions
        results = model(original_image_cv2)

        # Check if there are no detections
        if len(results[0].boxes.data) == 0:
            # Save the entire image to the processed images list
            processed_images.append({
                'question_index': current_question_index,
                'image_type': 'full',
                'image': original_image_cv2
            })
        else:
            # Sort detections based on y-coordinate (top to bottom)
            sorted_detections = sorted(results[0].boxes.data, key=lambda det: det[1])

            # Save from the top of the image to the topmost detection
            cut_image_top = original_image_cv2[:int(sorted_detections[0][1]), :]
            processed_images.append({
                'question_index': current_question_index,
                'image_type': 'top',
                'image': cut_image_top
            })
            current_question_index += 1

            # Save cut images between consecutive detections
            for i in range(len(sorted_detections)):
                if i == 0:
                    _, y_prev, _, _, _, _ = sorted_detections[i]
                    cut_image = original_image_cv2[int(y_prev):int(sorted_detections[i + 1][1]), :] if i + 1 < len(sorted_detections) else original_image_cv2[int(y_prev):, :]
                    processed_images.append({
                        'question_index': current_question_index,
                        'image_type': 'cut',
                        'image': cut_image
                    })
                    current_question_index += 1
                elif i == len(sorted_detections) - 1:
                    # Special case for the bottom-most detection
                    _, y_curr, _, _, _, _ = sorted_detections[i]
                    cut_image = original_image_cv2[int(y_curr):, :]
                    processed_images.append({
                        'question_index': current_question_index,
                        'image_type': 'cut',
                        'image': cut_image
                    })
                else:
                    _, y_prev, _, _, _, _ = sorted_detections[i]
                    _, y_curr, _, _, _, _ = sorted_detections[i + 1]
                    cut_image = original_image_cv2[int(y_prev):int(y_curr), :]

                    # Save the cut image to the processed images list
                    processed_images.append({
                        'question_index': current_question_index,
                        'image_type': 'cut',
                        'image': cut_image
                    })
                    current_question_index += 1

    # return a list of dictionaries containing each containing the keys : 'question_index', 'image_type', 'image'
    return processed_images


# diagram extractor

def extract_diagrams(processed_images, model_path):
    # Load the trained YOLOv8 model
    model = YOLO(model_path)

    # Initialize a list to store extracted diagram images and information
    extracted_diagrams = []

    # Iterate over each processed image dictionary
    for processed_image in processed_images:
        # Get the image data and information from the dictionary
        question_index = processed_image['question_index']
        image_type = processed_image['image_type']
        image = processed_image['image']

        # Make predictions on the image
        results = model(image)

        # Iterate over each detected object
        for det in results[0].boxes.data:
            # Get coordinates of the bounding box
            x, y, width, height, confidence, class_id = det.tolist()

            # Crop the region within the bounding box
            diagram_image = image[int(y):int(y + height), int(x):int(x + width)].copy()

            # Append the extracted diagram image and information to the list
            extracted_diagrams.append({
                'question_index': question_index,
                'image_type': image_type,
                'diagram_image': diagram_image
            })

    print("Diagrams extraction complete.")
    
    # return a list of dictionaries containing each containing the keys : 'question_index', 'image_type', 'diagram_image'
    return extracted_diagrams


# Main Point extractor

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the model
generation_config = {
  "temperature": 0.1,
  "top_p": 0.2,
  "top_k": 20,
}

gemini_vision = genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)

def generate_key_points(image):
    prompt = "You are acting as an intermediary between the student’s answer and the evaluator grading the students answer. You have been provided with an image of a student's answer sheet. Your objective is to thoroughly detect the handwritten text that the student has written and Extract the key points written by the student and output them word for word, DO NOT write your own output. If the image contains no relevant text output nothing."
    response = gemini_vision.generate_content([prompt, image], stream=True)
    response.resolve()

    # Access text from all parts and concatenate
    key_points = "".join(part.text for part in response.parts)

    return key_points


def process_and_extract_key_points(processed_images):
    extracted_key_points = []

    for image_data in processed_images:
        question_index = image_data['question_index']
        image_type = image_data['image_type']
        image_array = image_data['image']  # Assuming 'image' is a NumPy array

        # Convert the NumPy array to PIL.Image.Image
        image = Image.fromarray(np.uint8(image_array))

        key_points = generate_key_points(image)

        extracted_key_points.append({
            'question_index': question_index,
            'image_type': image_type,
            'key_points': key_points
        })

    # return a list of dictionaries containing each containing the keys : 'question_index', 'image_type', 'key_points'
    return extracted_key_points

# saving files
def save(var, output_filename, keys):
    data_to_save = [{key: item[key] for key in keys} for item in var]
    with open(output_filename, 'wb') as file:
        pickle.dump(data_to_save, file)

def save_combined_data(combined_data, output_filename):
    with open(output_filename, 'wb') as file:
        pickle.dump(combined_data, file)


# combining all variables into 1
def combine_data(processed_images, extracted_diagrams, extracted_key_points):
    combined_data = {}

    # Combine processed_images
    for item in processed_images:
        question_index = item['question_index']
        if question_index not in combined_data:
            combined_data[question_index] = {'processed_images': [], 'extracted_diagrams': [], 'extracted_key_points': []}
        combined_data[question_index]['processed_images'].append(item)

    # Combine extracted_diagrams
    for item in extracted_diagrams:
        question_index = item['question_index']
        if question_index not in combined_data:
            combined_data[question_index] = {'processed_images': [], 'extracted_diagrams': [], 'extracted_key_points': []}
        combined_data[question_index]['extracted_diagrams'].append(item)

    # Combine extracted_key_points
    for item in extracted_key_points:
        question_index = item['question_index']
        if question_index not in combined_data:
            combined_data[question_index] = {'processed_images': [], 'extracted_diagrams': [], 'extracted_key_points': []}
        combined_data[question_index]['extracted_key_points'].append(item)

    # dictionary with keys as question number
    return combined_data

# processed_images = process_pdf(input_pdf=upload_file, model_path='model2/train-2/weights/best.pt')
# # print(processed_images[0],"-------------------")
# # save(var=processed_images, output_filename="processed_images.pkl", keys=['question_index', 'image_type', 'image'])

# extracted_diagrams = extract_diagrams(processed_images, model_path="model/train/weights/best.pt")
# # print(extracted_diagrams[0],"-------------------")
# # save(var=extracted_diagrams, output_filename="extracted_diagrams.pkl", keys=['question_index', 'image_type', 'diagram_image'])


# extracted_key_points = process_and_extract_key_points(processed_images)
# # print(extracted_key_points[0],"-------------------")
# # save(var=extracted_key_points, output_filename="extracted_key_points.pkl", keys=['question_index', 'image_type', 'key_points'])


# combined_data = combine_data(processed_images, extracted_diagrams, extracted_key_points)
# # save_combined_data(combined_data, "combined_data.pkl")
