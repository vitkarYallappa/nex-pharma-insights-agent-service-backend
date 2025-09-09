from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


def setup_cors(app: FastAPI):
    """Setup CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on your needs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 