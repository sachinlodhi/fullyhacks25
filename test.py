from gradio_client import Client
import requests
import os

# Download a test image
url = 'https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'
response = requests.get(url)
os.makedirs('temp', exist_ok=True)
file_path = 'temp/test_bus.png'
    
with open(file_path, 'wb') as f:
    f.write(response.content)
    
print(f"Downloaded test image to {file_path}")

# Initialize client
print("Initializing client...")
client = Client("https://f5ad19aefcf9804c16.gradio.live/")

# Create file dictionary
file_dict = {
    "url": url,  # Using URL instead of local path
    "mime_type": "image/png"
}

# Make prediction
print("Making prediction...")
result = client.predict(
    input_image=file_dict,
    model_name="Stable Diffusion Upscaler (4x)",
    preset="General Astronomy",
    custom_prompt=None,
    noise_level=20,
    scientific_mode=False,
    api_name="/enhance_image"
)

print("Prediction complete!")
print(f"Result type: {type(result)}")