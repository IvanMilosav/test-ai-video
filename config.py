import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # Google AI configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    # Vertex AI configuration (for video generation)
    VERTEX_PROJECT_ID = os.getenv('VERTEX_PROJECT_ID')
    VERTEX_LOCATION = os.getenv('VERTEX_LOCATION', 'us-central1')
    
    # Video processing configuration
    MAX_HEIGHT = 720
    TEMP_DIR = '/tmp/video_processing'
    
    # Cloud Run job parameters
    VIDEO_URL = os.getenv('VIDEO_URL', '').strip()
    
    # Load analysis prompt from file if available, otherwise use default
    ANALYSIS_PROMPT = None
    
    @classmethod
    def get_analysis_prompt(cls):
        if cls.ANALYSIS_PROMPT is None:
            try:
                with open('config_files/prompt.txt', 'r') as f:
                    cls.ANALYSIS_PROMPT = f.read().strip()
            except:
                cls.ANALYSIS_PROMPT = os.getenv('ANALYSIS_PROMPT', '''
                Fill in this JSON schema using analysis from the video. Respond with only correct JSON, be as accurate as possible.
                
                { "primary_vertical": "string", "creator_username": "string", "hook_type": "string" }
                ''')
        return cls.ANALYSIS_PROMPT
    
    @classmethod
    def validate(cls):
        """Validate required environment variables"""
        required_vars = ['GOOGLE_API_KEY', 'VERTEX_PROJECT_ID']
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}. Please check your .env file.")