"""
Video Player Service for playing sign videos
"""
import json
import cv2
import time
from pathlib import Path
from desktop_app.config import Config


class VideoPlayer:
    """Manages video playback for sign glosses"""
    
    def __init__(self):
        """Initialize video player and load gloss index"""
        self.gloss_index = {}
        self.load_index()
    
    def load_index(self):
        """Load gloss video index from JSON"""
        try:
            with open(Config.GLOSA_INDEX_PATH, 'r', encoding='utf-8') as f:
                self.gloss_index = json.load(f)
            print(f"[VIDEO] Loaded {len(self.gloss_index)} glosses from index")
        except Exception as e:
            print(f"[VIDEO] Error loading index: {e}")
            self.gloss_index = {}
    
    def get_video_path(self, gloss: str) -> Path | None:
        """
        Get absolute path to video file for a gloss
        
        Args:
            gloss: Gloss name (e.g., "HOLA")
        
        Returns:
            Path to video file or None if not found
        """
        gloss_upper = gloss.upper()
        
        if gloss_upper not in self.gloss_index:
            return None
        
        video_data = self.gloss_index[gloss_upper]
        rel_path = video_data.get('path', '')
        
        if not rel_path:
            return None
        
        abs_path = Config.PROJECT_ROOT / rel_path
        
        if not abs_path.exists():
            print(f"[VIDEO] File not found: {abs_path}")
            return None
        
        return abs_path
    
    def play_video(self, video_path: Path, window_name: str = "Sign Video", 
                   playback_speed: float = 0.8):
        """
        Play a single video file
        
        Args:
            video_path: Path to video file
            window_name: Name for OpenCV window
            playback_speed: Playback speed multiplier (0.8 = slower)
        
        Returns:
            True if played successfully, False if interrupted
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            print(f"[VIDEO] Could not open: {video_path}")
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        delay = int((1000 / fps) / playback_speed)  # Adjust for playback speed
        
        print(f"[VIDEO] Playing: {video_path.name}")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            cv2.imshow(window_name, frame)
            
            # Wait with ability to interrupt
            if cv2.waitKey(delay) & 0xFF == ord('q'):
                cap.release()
                return False
        
        cap.release()
        time.sleep(0.3)  # Small delay between videos
        return True
    
    def play_sequence(self, glosses: list[str], window_name: str = "Sign Video"):
        """
        Play a sequence of sign videos
        
        Args:
            glosses: List of gloss names
            window_name: Name for OpenCV window
        
        Returns:
            Number of videos successfully played
        """
        if not glosses:
            return 0
        
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        
        played_count = 0
        
        for i, gloss in enumerate(glosses):
            print(f"[VIDEO] Playing {i+1}/{len(glosses)}: {gloss}")
            
            video_path = self.get_video_path(gloss)
            
            if video_path is None:
                print(f"[VIDEO] No video found for: {gloss}")
                # Show text placeholder for 2 seconds
                placeholder = self.create_text_frame(f"Señal: {gloss}")
                cv2.imshow(window_name, placeholder)
                if cv2.waitKey(2000) & 0xFF == ord('q'):
                    break
                continue
            
            # Play video
            if not self.play_video(video_path, window_name):
                break  # User pressed 'q'
            
            played_count += 1
        
        cv2.destroyWindow(window_name)
        return played_count
    
    def create_text_frame(self, text: str, width: int = 640, height: int = 480):
        """Create a frame with centered text"""
        import numpy as np
        
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (30, 41, 59)  # Dark blue background
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 2
        
        # Get text size
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Center text
        x = (width - text_width) // 2
        y = (height + text_height) // 2
        
        cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness)
        
        return frame


# Global instance
video_player = VideoPlayer()
