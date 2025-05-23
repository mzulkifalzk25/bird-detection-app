from PIL import Image
from transformers import pipeline

# Path to your local image (update this to the actual file path)
image_path = "./crow.jpeg"

# Open the image
img = Image.open(image_path).convert("RGB")  # Ensure it's in RGB mode

# Load the bird classification model
pipe = pipeline("image-classification", model="dennisjooo/Birds-Classifier-EfficientNetB2")

# Run inference
result = pipe(img)[0]

# Print the result
print("Predicted bird species:", result['label'])
