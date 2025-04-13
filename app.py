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

# Custom CSS for styling including magnifying glass and space background
st.markdown("""
<style>
    body {
        background-color: #070B34;
        background-image: 
            radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
            radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
            radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px),
            radial-gradient(rgba(255,255,255,.4), rgba(255,255,255,.1) 2px, transparent 30px);
        background-size: 550px 550px, 350px 350px, 250px 250px, 150px 150px;
        background-position: 0 0, 40px 60px, 130px 270px, 70px 100px;
        animation: starsAnimation 200s linear infinite;
    }

    @keyframes starsAnimation {
        0% {
            background-position: 0 0, 40px 60px, 130px 270px, 70px 100px;
        }
        100% {
            background-position: 550px 550px, 390px 410px, 380px 520px, 220px 250px;
        }
    }

    .main-header {
        font-size: 2.5rem;
        color: #8EB8E5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(142, 184, 229, 0.5);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #5D9CEC;
        margin-bottom: 1rem;
        font-weight: 500;
        text-shadow: 0 0 5px rgba(93, 156, 236, 0.3);
    }
    
    .stImage {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
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
        background-color: #5D9CEC;
    }
    
    .result-container {
        background-color: rgba(10, 20, 50, 0.7);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(93, 156, 236, 0.3);
    }
    
    .footer {
        text-align: center;
        color: #5D9CEC;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
    
    .stSidebar {
        background-color: rgba(10, 20, 50, 0.7);
    }
    
    /* Image comparison container */
    .comparison-container {
        position: relative;
        overflow: hidden;
        width: 100%;
        height: auto;
        border-radius: 10px;
    }
    
    /* Magnifier glass styling */
    .img-magnifier-glass {
        position: absolute;
        border: 3px solid #5D9CEC;
        border-radius: 50%;
        cursor: none;
        /*Set the size of the magnifier glass:*/
        width: 150px;
        height: 150px;
        box-shadow: 0 0 10px 2px rgba(93, 156, 236, 0.5);
    }
    
    .st-emotion-cache-1v0mbdj {
        background-color: rgba(10, 20, 50, 0.7);
    }
    
    .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3,
    .st-emotion-cache-16txtl3 h4, .st-emotion-cache-16txtl3 h5, .st-emotion-cache-16txtl3 h6,
    .st-emotion-cache-16txtl3 p, .st-emotion-cache-16txtl3 li {
        color: #C8E0F4;
    }
    
    .st-emotion-cache-16txtl3 a {
        color: #5D9CEC;
    }
    
    /* Main content area */
    .st-emotion-cache-z5fcl4 {
        background-color: rgba(7, 11, 52, 0.8);
        padding: 2rem;
        border-radius: 15px;
        backdrop-filter: blur(5px);
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for magnifying glass functionality
st.markdown("""
<script>
function magnify(imgId, resultImgId, zoom) {
  var img, glass, w, h, bw;
  img = document.getElementById(imgId);
  
  /* Create magnifier glass: */
  glass = document.createElement("DIV");
  glass.setAttribute("class", "img-magnifier-glass");
  
  /* Insert magnifier glass: */
  img.parentElement.insertBefore(glass, img);
  
  /* Set background properties for the magnifier glass: */
  glass.style.backgroundImage = "url('" + document.getElementById(resultImgId).src + "')";
  glass.style.backgroundRepeat = "no-repeat";
  glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
  
  /* Set size of glass: */
  glass.style.width = "150px";
  glass.style.height = "150px";
  
  /* Execute a function when someone moves the magnifier glass over the image: */
  glass.addEventListener("mousemove", moveMagnifier);
  img.addEventListener("mousemove", moveMagnifier);
  
  /* Also for touch screens: */
  glass.addEventListener("touchmove", moveMagnifier);
  img.addEventListener("touchmove", moveMagnifier);
  
  function moveMagnifier(e) {
    var pos, x, y;
    /* Prevent any other actions that may occur when moving over the image */
    e.preventDefault();
    
    /* Get the cursor's x and y positions: */
    pos = getCursorPos(e);
    x = pos.x;
    y = pos.y;
    
    /* Prevent the magnifier glass from being positioned outside the image: */
    if (x > img.width - (glass.offsetWidth / zoom)) {x = img.width - (glass.offsetWidth / zoom);}
    if (x < glass.offsetWidth / zoom) {x = glass.offsetWidth / zoom;}
    if (y > img.height - (glass.offsetHeight / zoom)) {y = img.height - (glass.offsetHeight / zoom);}
    if (y < glass.offsetHeight / zoom) {y = glass.offsetHeight / zoom;}
    
    /* Set the position of the magnifier glass: */
    glass.style.left = (x - glass.offsetWidth / 2) + "px";
    glass.style.top = (y - glass.offsetHeight / 2) + "px";
    
    /* Display what the magnifier glass "sees": */
    glass.style.backgroundPosition = "-" + ((x * zoom) - glass.offsetWidth / 2) + "px -" + ((y * zoom) - glass.offsetHeight / 2) + "px";
  }
  
  function getCursorPos(e) {
    var a, x = 0, y = 0;
    e = e || window.event;
    
    /* Get the x and y positions of the image: */
    a = img.getBoundingClientRect();
    
    /* Calculate the cursor's x and y coordinates, relative to the image: */
    x = e.pageX - a.left;
    y = e.pageY - a.top;
    
    /* Consider any page scrolling: */
    x = x - window.pageXOffset;
    y = y - window.pageYOffset;
    return {x : x, y : y};
  }
}

// Function to initialize the magnifying glass when images are loaded
document.addEventListener('DOMContentLoaded', function() {
  // Check every second if the images are loaded
  var checkImagesInterval = setInterval(function() {
    var origImg = document.getElementById('original-image');
    var enhancedImg = document.getElementById('enhanced-image');
    
    if (origImg && enhancedImg) {
      clearInterval(checkImagesInterval);
      setTimeout(function() {
        magnify("original-image", "enhanced-image", 1);
      }, 1000); // Small delay to ensure images are fully rendered
    }
  }, 1000);
});
</script>
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

# Header with space theme styling
st.markdown("<h1 class='main-header'>🔭 Astronomy Image Enhancer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A7C7E7; margin-bottom: 2rem;'>Transform your astronomy images with AI-powered enhancement tools</p>", unsafe_allow_html=True)

# Initialize session state for storing results
if 'enhanced_image' not in st.session_state:
    st.session_state.enhanced_image = None
if 'enhancement_prompt' not in st.session_state:
    st.session_state.enhancement_prompt = None
if 'before_after' not in st.session_state:
    st.session_state.before_after = None
if 'timestamp' not in st.session_state:
    st.session_state.timestamp = None

# Sidebar for inputs with space theme
with st.sidebar:
    st.markdown("<h2 class='sub-header'>🚀 Enhancement Settings</h2>", unsafe_allow_html=True)
    
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
    process_button = st.button("✨ Enhance Image", use_container_width=True)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h2 class='sub-header'>Original Image</h2>", unsafe_allow_html=True)
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # Save the image to a bytes buffer and convert to base64 for HTML display
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Display the image with an ID using HTML
        st.markdown(f'''
        <div style="width:100%;">
            <img src="data:image/png;base64,{img_str}" id="original-image" 
                style="width:100%; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.info("Please upload an image to enhance")

with col2:
    st.markdown("<h2 class='sub-header'>Enhanced Result</h2>", unsafe_allow_html=True)
    if st.session_state.enhanced_image is not None:
        # Save the enhanced image to a bytes buffer and convert to base64 for HTML display
        buffered = io.BytesIO()
        st.session_state.enhanced_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Display the image with an ID using HTML
        st.markdown(f'''
        <div style="width:100%;">
            <img src="data:image/png;base64,{img_str}" id="enhanced-image" 
                style="width:100%; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        </div>
        ''', unsafe_allow_html=True)
        
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
    with st.spinner("✨ Enhancing your image... Please wait, this may take a minute."):
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

# Magnifying glass comparison (only if we have results)
if st.session_state.enhanced_image is not None and uploaded_file is not None:
    st.markdown("<h2 class='sub-header'>🔍 Magnifying Glass Comparison</h2>", unsafe_allow_html=True)
    st.markdown("<p>Hover over the original image to see a detailed comparison with the enhanced version</p>", unsafe_allow_html=True)
    
    # Create two columns for the comparison
    comp_cols = st.columns([1, 1])
    with comp_cols[0]:
        # Create a container for the original image with hover functionality
        st.markdown('<div class="comparison-container">', unsafe_allow_html=True)
        
        # Use the session state to get the original image and convert to base64
        image = Image.open(uploaded_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Display the image with HTML
        st.markdown(f'''
        <img src="data:image/png;base64,{img_str}" id="magnify-original" 
            style="width:100%; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Original Image - Hover to compare")
    
    with comp_cols[1]:
        # Display the enhanced image (used by the magnifier) using HTML
        buffered = io.BytesIO()
        st.session_state.enhanced_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown(f'''
        <img src="data:image/png;base64,{img_str}" id="magnify-enhanced" 
            style="width:100%; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        ''', unsafe_allow_html=True)
        st.caption("Enhanced Image")
    
    # JavaScript to activate the magnifying glass
    st.markdown("""
    <script>
        // Wait for the DOM to be fully loaded
        setTimeout(function() {
            // Initialize magnify function
            var origImg = document.getElementById('magnify-original');
            var enhancedImg = document.getElementById('magnify-enhanced');
            
            if (origImg && enhancedImg) {
                magnify("magnify-original", "magnify-enhanced", 1);
            }
        }, 2000);  // Added delay to ensure elements are loaded
    </script>
    """, unsafe_allow_html=True)

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
        label="📥 Download Enhanced Image",
        data=buffered.getvalue(),
        file_name=f"enhanced_image_{st.session_state.timestamp.replace(' ', '_').replace(':', '-')}.png",
        mime="image/png",
        use_container_width=True
    )

# Add an HTML component to ensure the JavaScript for magnifying glass is properly loaded
st.components.v1.html("""
<script>
// This is a trigger to make sure our JavaScript runs after all images are loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
});

// Additional event listener for images
window.addEventListener('load', function() {
    console.log('All resources loaded');
    
    // Try to initialize magnifier after a delay
    setTimeout(function() {
        try {
            var origImg = document.getElementById('original-image');
            var enhancedImg = document.getElementById('enhanced-image');
            
            if (origImg && enhancedImg) {
                console.log('Images found, initializing magnifier');
                magnify("original-image", "enhanced-image", 1);
            } else {
                console.log('Images not found yet');
            }
        } catch (e) {
            console.error('Error initializing magnifier:', e);
        }
    }, 3000);
});
</script>
""", height=0)

# Footer with space theme
st.markdown("<div class='footer'>✨ Powered by AI Image Enhancement Technology ✨</div>", unsafe_allow_html=True)