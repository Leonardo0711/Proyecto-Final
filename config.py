"""
Configuration Management for Desktop App
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from desktop_app directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration"""
    
    # Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Paths
    PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT', ''))
    VIDEOS_DIR = Path(os.getenv('VIDEOS_DIR', ''))
    GLOSA_INDEX_PATH = Path(os.getenv('GLOSA_INDEX_PATH', ''))
    MODEL_DIR = Path(os.getenv('MODEL_DIR', ''))
    
    # Camera (matching realtime_inference.py)
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', 0))
    FRAME_WIDTH = int(os.getenv('FRAME_WIDTH', 960))
    FRAME_HEIGHT = int(os.getenv('FRAME_HEIGHT', 540))
    
    # FSM Parameters (matching realtime_inference.py)
    START_STREAK = 4
    END_STREAK = 6
    MIN_SIGN_FRAMES = 12
    MAX_SIGN_FRAMES = 96
    MIN_CONFIDENCE = 0.4
    
    # Model Parameters
    MAX_LEN = 64
    D_MODEL = 256
    N_HEADS = 8
    N_LAYERS = 6
    DIM_FF = 1024
    DROPOUT = 0.1
    DROP_PATH = 0.1
    
    # MediaPipe
    MP_MODEL_COMPLEX = 1
    MP_MIN_DET = 0.65
    MP_MIN_TRK = 0.65
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        if not cls.MODEL_DIR.exists():
            raise ValueError(f"MODEL_DIR not found: {cls.MODEL_DIR}")
        if not cls.GLOSA_INDEX_PATH.exists():
            raise ValueError(f"GLOSA_INDEX_PATH not found: {cls.GLOSA_INDEX_PATH}")
        return True
