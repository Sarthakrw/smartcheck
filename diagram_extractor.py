from IPython.display import Image, display
import cv2
import os
from ultralytics import YOLO

# Load the trained YOLOv8 model
model = YOLO("model/train/weights/best.pt")

# Folder containing images
input_folder = "test/CBSE-Topper-Answer-Sheet-Class-12-Maths-2018"

# Output folder for images with bounding boxes
output_folder = "output_images"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate over each file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
        # Load the image
        image_path = os.path.join(input_folder, filename)
        original_image = cv2.imread(image_path)

        # Make predictions
        results = model(image_path)

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
