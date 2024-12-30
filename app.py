import streamlit as st
import google.generativeai as genai
from gradio_client import Client
from PIL import Image
import io
import os
import tempfile
import base64
import requests
import time

def get_image_prompts(story, api_key):
    """Generate image prompts from the story using Google's Generative AI."""
    # Configure the API
    genai.configure(api_key=api_key)
    
    template = """
    You are an expert in understanding the depth of the story, its characters, and places.
    You excel at splitting a story into 10 meaningful sentences in order.
    Here is the story: {story}

    We have a project in which the teachers give us a story and we need to display them in 10 pictures. 
    The pictures must be storyly connected to each other in the cartoon form.
    Your task is to split it into 10 meaningful sentences in order and generate an image prompt for each sentence.
    Ensure every image prompt captures the essence of the scene, defining character types and designs, 
    climate conditions, and all essential details to represent the story visually at every single step.

    Note: The prompt for each image must be 100 to 150 words with clear prompt for image generation.
    Note: At every prompt describe how the characters look and mention the places, background, and climate.
    Note: Disney mode

    Please return the output exactly in this format with no additional text:
    list = [
        ["scene1 description", "character style", "key elements", "mood"],
        ["scene2 description", "character style", "key elements", "mood"],
        ... up to 10 scenes
    ]
    """
    
    final_prompt = template.format(story=story)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(final_prompt)
    
    try:
        local_dict = {}
        exec(response.text, {}, local_dict)
        return local_dict.get('list', [])
    except Exception as e:
        st.error(f"Error processing AI response: {str(e)}")
        return []

def generate_image(prompt, client):
    """Generate a single image using the FLUX model."""
    try:
        result = client.predict(
            prompt=prompt[0],  # Using the scene description
            seed=0,
            randomize_seed=True,
            width=1024,
            height=576,
            num_inference_steps=4,
            api_name="/infer"
        )
        return Image.open(result[0])
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

def get_image_download_link(img, filename, text):
    """Generate a link to download the image."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

def main():
    st.set_page_config(layout="wide", page_title="Story Visualizer")
    
    st.title("✨ Story Visualization Generator")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Generate Story", "View Gallery"])
    
    with tab1:
        # Sidebar for API configuration
        with st.sidebar:
            st.header("🔑 API Configuration")
            google_api_key = st.text_input("Google AI API Key", type="password")
            hf_token = st.text_input("Hugging Face Token", type="password")
            
            if 'generated_images' not in st.session_state:
                st.session_state.generated_images = []
                st.session_state.prompts = []
        
        # Main content
        st.header("📝 Enter Your Story")
        story = st.text_area("Type or paste your story here:", height=200)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            generate_button = st.button("✨ Generate")
        
        if generate_button:
            if not story:
                st.error("Please enter a story first.")
                return
            
            if not google_api_key or not hf_token:
                st.error("Please provide both API keys in the sidebar.")
                return
            
            try:
                # Generate prompts
                with st.spinner("🤖 Generating image prompts..."):
                    prompts = get_image_prompts(story, google_api_key)
                    st.session_state.prompts = prompts
                
                if prompts:
                    # Initialize FLUX client
                    os.environ['HF_TOKEN'] = hf_token
                    client = Client("black-forest-labs/FLUX.1-schnell")
                    
                    # Create a progress container
                    progress_container = st.container()
                    progress_bar = st.progress(0)
                    
                    # Generate and display images one by one
                    st.session_state.generated_images = []
                    
                    for idx, prompt in enumerate(prompts):
                        progress_container.text(f"Generating image {idx + 1} of {len(prompts)}...")
                        
                        # Generate image
                        image = generate_image(prompt, client)
                        if image:
                            st.session_state.generated_images.append(image)
                            
                            # Display image and details
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.image(image, caption=f"Scene {idx + 1}", use_column_width=True)
                                st.markdown(get_image_download_link(image, f"scene_{idx+1}.png", "📥 Download Image"), unsafe_allow_html=True)
                            with col2:
                                st.write("*Scene Description:*")
                                st.write(prompt[0])
                                st.write("*Style:*", prompt[1])
                                st.write("*Key Elements:*", prompt[2])
                                st.write("*Mood:*", prompt[3])
                            
                            st.divider()
                        
                        # Update progress
                        progress_bar.progress((idx + 1) / len(prompts))
                    
                    progress_container.success("✅ All images generated successfully!")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    with tab2:
        if st.session_state.generated_images:
            st.header("🖼 Generated Images Gallery")
            
            # Display images in a grid
            cols = st.columns(2)
            for idx, (image, prompt) in enumerate(zip(st.session_state.generated_images, st.session_state.prompts)):
                with cols[idx % 2]:
                    st.image(image, caption=f"Scene {idx + 1}", use_column_width=True)
                    with st.expander("Scene Details"):
                        st.write("*Description:*", prompt[0])
                        st.write("*Style:*", prompt[1])
                        st.write("*Key Elements:*", prompt[2])
                        st.write("*Mood:*", prompt[3])
                    st.markdown(get_image_download_link(image, f"scene_{idx+1}.png", "📥 Download Image"), unsafe_allow_html=True)
        else:
            st.info("No images generated yet. Go to the Generate Story tab to create some!")

if __name__ == "__main__":
    main()
