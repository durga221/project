# Story Visualizer

A Streamlit application that transforms written stories into sequences of AI-generated images.

## Description

Story Visualizer uses Google's Gemini AI and FLUX image generation model to convert text narratives into visual sequences. The application breaks down stories into 10 key scenes and generates corresponding images with detailed prompts.

## Features

- Story text input interface
- Automatic scene breakdown and prompt generation
- Image generation with FLUX model
- Image gallery view
- Download capability for generated images
- Detailed scene descriptions and metadata

## Usage

1. Launch the application:
```bash
streamlit run app.py
```

2. Navigate to the Generate Story tab
3. Enter your story in the text area
4. Click Generate to create image sequence
5. View and download generated images from the Gallery tab

## Architecture

### Component Overview
- Frontend: Streamlit web interface
- Story Analysis: Google Gemini AI
- Image Generation: FLUX model via Hugging Face
- State Management: Streamlit session state

### Data Flow
1. Story Input
   - User submits story text through Streamlit interface
   - API keys validated and stored securely

2. Prompt Generation
   - Story sent to Gemini AI
   - AI breaks story into 10 scenes
   - Each scene converted to detailed image prompts
   - Prompts include scene description, style, elements, and mood

3. Image Generation
   - FLUX model processes prompts sequentially
   - Generated images stored in session state
   - Progress tracked and displayed to user

4. Image Display and Storage
   - Images rendered in main view
   - Gallery view maintains image-prompt relationships
   - Base64 encoding enables direct downloads

### Key Components
```
app/
├── main.py           # Main application file
├── functions/
│   ├── prompt_generation.py    # Gemini AI integration
│   ├── image_generation.py     # FLUX model integration
│   └── utils.py               # Helper functions
├── ui/
│   ├── main_view.py          # Story input interface
│   └── gallery.py           # Image gallery interface
└── config/
    └── settings.py          # Configuration management
```

## Technical Implementation

- Uses Google's Gemini AI for story analysis and prompt generation
- Implements FLUX model for image generation
- Streamlit for the web interface
- Base64 encoding for image downloads
- Session state management for gallery persistence
