"""Hugging Face Spaces entry point for the Gradio demo.

This file is required by Hugging Face Spaces to launch the Gradio interface.
"""
from demo_gradio import demo

# Launch the demo for Hugging Face Spaces
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False
)