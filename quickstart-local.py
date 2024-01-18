from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import time

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your subscription key and endpoint from environment variables
subscription_key = os.environ["VISION_KEY"]
endpoint = os.environ["VISION_ENDPOINT"]

# Create an instance of ComputerVisionClient
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Specify the path to your image
read_image_path = "images/answer_sheet.png"

# Open the image in binary mode
with open(read_image_path, "rb") as read_image:
    # Call the API with the image and raw response (allows you to get the operation location)
    read_response = computervision_client.read_in_stream(read_image, raw=True)

    # Get the operation location (URL with ID as the last appendage)
    read_operation_location = read_response.headers["Operation-Location"]
    # Extract the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for the retrieval of the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower() not in ['notstarted', 'running']:
            break
        print('Waiting for result...')
        time.sleep(10)

    # Print results, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                print(line.text)
                #print(line.bounding_box)
    print()

# End of Computer Vision quickstart
print("End of Computer Vision quickstart.")
