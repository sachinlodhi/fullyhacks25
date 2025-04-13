import streamlit as st
import requests
import io
import base64
from PIL import Image
import tempfile
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Astronomy Image Enhancer",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A6572;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #344955;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton button {
        background-color: #4A6572;
        color: white;
        font-weight: 500;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #344955;
    }
    .result-container {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
    .stSidebar {
        background-color: #f5f7fa;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_URL = "https://248f-132-249-252-216.ngrok-free.app"  # FastAPI server URL

# Functions to interact with the API
def get_models():
    """Get available models from the API"""
    try:
        response = requests.get(f"{API_URL}/models")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching models: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_presets():
    """Get available presets from the API"""
    try:
        response = requests.get(f"{API_URL}/presets")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching presets: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def enhance_image(image_file, model_name, preset, custom_prompt, noise_level, scientific_mode):
    """Send image to API for enhancement"""
    try:
        # Create the form data
        files = {"image": (image_file.name, image_file, "image/png")}
        data = {
            "model_name": model_name,
            "preset": preset,
            "noise_level": noise_level,
            "scientific_mode": str(scientific_mode).lower()
        }
        
        # Add custom prompt if it exists
        if custom_prompt:
            data["custom_prompt"] = custom_prompt
            
        # Make the request
        response = requests.post(f"{API_URL}/enhance_image", files=files, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error enhancing image: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def base64_to_image(base64_str):
    """Convert base64 string to PIL Image"""
    # Remove data URL prefix if present
    if "base64," in base64_str:
        base64_str = base64_str.split("base64,")[1]
    
    image_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_bytes))

# Header
st.markdown("<h1 class='main-header'>🔭 Astronomy Image Enhancer</h1>", unsafe_allow_html=True)
st.markdown("Transform your astronomy images with AI-powered enhancement tools")

# Initialize session state for storing results
if 'enhanced_image' not in st.session_state:
    st.session_state.enhanced_image = None
if 'enhancement_prompt' not in st.session_state:
    st.session_state.enhancement_prompt = None
if 'before_after' not in st.session_state:
    st.session_state.before_after = None
if 'timestamp' not in st.session_state:
    st.session_state.timestamp = None

# Sidebar for inputs
with st.sidebar:
    st.markdown("<h2 class='sub-header'>Enhancement Settings</h2>", unsafe_allow_html=True)
    
    # Image upload
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    # Get models from API
    models = get_models()
    if not models:
        models = [
            "Stable Diffusion Upscaler (4x)",
            "ESRGAN Plus (4x)",
            "SwinIR (4x)",
            "Codeformer (Face Enhancement)",
            "Real-ESRGAN (4x)"
        ]
    
    # Model selection
    model_name = st.selectbox(
        "Upscaler Model",
        models
    )
    
    # Get presets from API
    presets = get_presets()
    if not presets:
        presets = [
            "General Astronomy",
            "Galaxy",
            "Nebula",
            "Planet",
            "Star Cluster", 
            "Solar Surface",
            "Black Hole",
            "Deep Field",
            "Scientific Accuracy"
        ]
    
    # Preset selection
    preset = st.selectbox(
        "Preset Enhancement Type",
        presets
    )
    
    # Custom prompt
    custom_prompt = st.text_area("Custom Enhancement Description (optional)")
    if custom_prompt == "":
        custom_prompt = None
    
    # Noise level
    noise_level = st.slider("Noise Level", min_value=0.0, max_value=50.0, value=20.0, 
                          help="Higher = more creative, lower = more faithful")
    
    # Scientific mode
    scientific_mode = st.checkbox("Scientific Accuracy Mode", 
                               help="Prevents artificial additions")
    
    # Process button
    process_button = st.button("Enhance Image", use_container_width=True)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h2 class='sub-header'>Original Image</h2>", unsafe_allow_html=True)
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
    else:
        st.info("Please upload an image to enhance")

with col2:
    st.markdown("<h2 class='sub-header'>Enhanced Result</h2>", unsafe_allow_html=True)
    if st.session_state.enhanced_image is not None:
        st.image(st.session_state.enhanced_image, use_column_width=True)
        
        # Display timestamp
        if st.session_state.timestamp:
            st.caption(f"Enhanced on: {st.session_state.timestamp}")
            
        # Display prompt used
        if st.session_state.enhancement_prompt:
            with st.expander("Enhancement Prompt Used"):
                st.write(st.session_state.enhancement_prompt)
    else:
        st.info("Enhanced image will appear here")

# Process the image when button is clicked
if uploaded_file is not None and process_button:
    with st.spinner("Enhancing your image... Please wait, this may take a minute."):
        try:
            # Reset the file pointer to the beginning
            uploaded_file.seek(0)
            
            # Send to API for enhancement
            result = enhance_image(
                uploaded_file,
                model_name,
                preset,
                custom_prompt,
                noise_level,
                scientific_mode
            )
            
            if result:
                # Extract data from API response
                enhanced_image_base64 = result["enhanced_image"]
                enhancement_prompt = result["prompt_used"]
                before_after_base64 = result["before_after"]
                
                # Convert base64 to images
                enhanced_image = base64_to_image(enhanced_image_base64)
                before_after_images = [base64_to_image(img) for img in before_after_base64]
                
                # Store results in session state
                st.session_state.enhanced_image = enhanced_image
                st.session_state.enhancement_prompt = enhancement_prompt
                st.session_state.before_after = before_after_images
                st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Trigger rerun to update the UI
                st.rerun()
            
        except Exception as e:
            st.error(f"Error enhancing image: {str(e)}")

# Before vs After comparison (only if we have results)
if st.session_state.before_after is not None:
    st.markdown("<h2 class='sub-header'>Before vs After Comparison</h2>", unsafe_allow_html=True)
    
    # Extract images from the before_after list
    if len(st.session_state.before_after) >= 2:
        cols = st.columns(2)
        with cols[0]:
            st.image(st.session_state.before_after[0], caption="Original", use_column_width=True)
        with cols[1]:
            st.image(st.session_state.before_after[1], caption="Enhanced", use_column_width=True)

# Add download button if enhanced image exists
if st.session_state.enhanced_image is not None:
    buffered = io.BytesIO()
    st.session_state.enhanced_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    st.download_button(
        label="Download Enhanced Image",
        data=buffered.getvalue(),
        file_name=f"enhanced_image_{st.session_state.timestamp.replace(' ', '_').replace(':', '-')}.png",
        mime="image/png",
        use_container_width=True
    )

# Footer
st.markdown("<div class='footer'>Powered by AI Image Enhancement Technology</div>", unsafe_allow_html=True)