import cv2
import os
from ultralytics import YOLO

# Load the trained YOLOv8 model
model = YOLO("model2/train-2/weights/best.pt")

# Folder containing images
input_folder = "test/CBSE-Topper-Answer-Sheet-Class-12-Biology-2016"

# Output folder for cut images
cut_images_folder = "cut_images"
os.makedirs(cut_images_folder, exist_ok=True)

# Iterate over each file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
        # Load the image
        image_path = os.path.join(input_folder, filename)
        original_image = cv2.imread(image_path)

        # Make predictions
        results = model(image_path)

        # Check if there are no detections
        if len(results[0].boxes.data) == 0:
            # Save the entire image
            entire_image_path = os.path.join(cut_images_folder, f"entire_{filename}")
            cv2.imwrite(entire_image_path, original_image)

        else:
            # Sort detections based on y-coordinate (top to bottom)
            detections = sorted(results[0].boxes.data, key=lambda det: det[1])

            # Save the regions between consecutive lines and from the last line to the bottom of the page
            for i in range(len(detections)):
                if i == 0:
                    # Save from the top of the image to the first line
                    cut_image = original_image[:int(detections[i][1]), :]
                    cut_image_path = os.path.join(cut_images_folder, f"cut_{i}_{filename}")
                    cv2.imwrite(cut_image_path, cut_image)
                else:
                    # Save from the current line to the next line or to the bottom of the page
                    _, y_prev, _, _, _, _ = detections[i - 1]
                    _, y_curr, _, _, _, _ = detections[i]
                    cut_image = original_image[int(y_prev):int(y_curr), :]
                    cut_image_path = os.path.join(cut_images_folder, f"cut_{i}_{filename}")
                    cv2.imwrite(cut_image_path, cut_image)

            # If there are detections, save from the last line to the bottom of the page
            _, y_last, _, _, _, _ = detections[-1]
            last_line_cut_image = original_image[int(y_last):, :]
            last_line_cut_image_path = os.path.join(cut_images_folder, f"cut_last_{filename}")
            cv2.imwrite(last_line_cut_image_path, last_line_cut_image)
