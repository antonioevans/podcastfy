"""Server Runner Module"""
import uvicorn
from podcastfy.webhook_handler import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
