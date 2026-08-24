import uvicorn
from api.main import app

if __name__ == "__main__":
    # Hugging Face Spaces sets PORT=7860 by default for Gradio apps
    uvicorn.run(app, host="0.0.0.0", port=7860)
