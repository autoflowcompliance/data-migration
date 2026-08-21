"""Entry point for Gradio demo (works with both Hugging Face and Render)."""
import os
from demo_gradio import demo

# Use PORT environment variable for Render, default to 7860 for local/Hugging Face
port = int(os.environ.get("PORT", 7860))

# Launch the demo
demo.launch(
    server_name="0.0.0.0",
    server_port=port,
    share=False
)