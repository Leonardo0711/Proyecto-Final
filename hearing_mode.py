"""
Hearing Mode Window - Text to Signs
- Text input
- Video playback in UI
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
from desktop_app.gemini_service import natural_text_to_glosses
from desktop_app.video_player import video_player


class HearingModeWindow:
    """Hearing Mode: Text → Signs"""
    
    def __init__(self, parent_window, on_close_callback):
        self.parent = parent_window
        self.on_close = on_close_callback
        
        # Window
        self.window = tk.Toplevel(parent_window)
        self.window.title("Modo Oyente - Texto a Señas")
        self.window.geometry("1200x750")
        self.window.configure(bg='#0f172a')
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # State
        self.current_glosses = []
        self.is_playing = False
        
        self.create_ui()
    
    def create_ui(self):
        """Create responsive 2-column UI"""
         # Header - Modern
        header = tk.Frame(self.window, bg='#1e293b', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🗣️  Modo Oyente - Texto a Señas",
                font=("Inter", 24, "bold"), bg='#1e293b', fg='#f8fafc').pack(pady=25)
        
        # Main container (responsive 2 columns)
        main = tk.Frame(self.window, bg='#0f172a')
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # LEFT COLUMN (500px, not expandable)
        left = tk.Frame(main, bg='#0f172a', width=500)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left.pack_propagate(False)
        
        # Input label - Modern
        tk.Label(left, text="✍️ Escribe el texto a traducir:",
                font=("Inter", 13, "bold"), bg='#0f172a', fg='#e0e7ff').pack(anchor=tk.W, pady=(5, 8))
        
        # Text input - Modern
        self.text_input = scrolledtext.ScrolledText(
            left, font=("Inter", 13), bg='#1e293b', fg='#f8fafc',
            insertbackground='white', relief=tk.FLAT, height=8, wrap=tk.WORD, padx=12, pady=10
        )
        self.text_input.pack(fill=tk.X, pady=(0, 15))
        
        # Translate button - Modern and large
        tk.Button(
            left, text="🔄  Traducir a Señas",
            font=("Inter", 14, "bold"), bg='#10b981', fg='white',
            activebackground='#059669', activeforeground='white',
            relief=tk.FLAT, cursor='hand2', command=self.translate_text, padx=20, pady=15
        ).pack(fill=tk.X, pady=(0, 20))
        
        # Glosses section - Modern
        tk.Label(left, text="📝 Glosas Detectadas:",
                font=("Inter", 13, "bold"), bg='#0f172a', fg='#e0e7ff').pack(anchor=tk.W, pady=(15, 8))
        
        glosses_frame = tk.Frame(left, bg='#1e293b', height=100)
        glosses_frame.pack(fill=tk.X, pady=(0, 10))
        glosses_frame.pack_propagate(False)
        
        self.glosses_container = tk.Frame(glosses_frame, bg='#1e293b')
        self.glosses_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # RIGHT COLUMN (expandable video player)
        right = tk.Frame(main, bg='#1e293b')
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right, text="📹  Reproducción de Señas",
                font=("Inter", 16, "bold"), bg='#1e293b', fg='#e0e7ff').pack(pady=(20, 15))
        
        # Video display (responsive) - Modern
        self.video_display = tk.Label(
            right, bg='#0f172a',
            text="Los videos se reproducirán aquí automáticamente",
            font=("Inter", 12), fg='#94a3b8'
        )
        self.video_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        # Current gloss - Modern
        self.current_gloss_label = tk.Label(
            right, text="", font=("Inter", 18, "bold"),
            bg='#1e293b', fg='#10b981'
        )
        self.current_gloss_label.pack(pady=20)
        
        # Back button - Modern and larger
        back_frame = tk.Frame(self.window, bg='#0f172a', height=70)
        back_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=30, pady=15)
        back_frame.pack_propagate(False)
        
        tk.Button(
            back_frame, text="←  Volver al Menú Principal",
            font=("Inter", 12, "bold"), bg='#475569', fg='white',
            activebackground='#64748b', activeforeground='white',
            relief=tk.FLAT, cursor='hand2', command=self.close_window, padx=30, pady=12
        ).pack(expand=True)
    
    def translate_text(self):
        """Translate and auto-play"""
        text = self.text_input.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("Texto Vacío", "Escribe texto para traducir")
            return
        
        self.current_gloss_label.config(text="Traduciendo ...")
        
        def translate_bg():
            glosses = natural_text_to_glosses(text)
            self.window.after(0, lambda: self.display_glosses(glosses))
        
        threading.Thread(target=translate_bg, daemon=True).start()
    
    def display_glosses(self, glosses):
        """Display and auto-play"""
        # Clear
        for widget in self.glosses_container.winfo_children():
            widget.destroy()
        
        self.current_glosses = glosses
        
        if not glosses:
            self.current_gloss_label.config(text="No se encontraron glosas")
            return
        
        # Create modern badges
        for gloss in glosses:
            tk.Label(
                self.glosses_container, text=gloss,
                font=("Inter", 12, "bold"), bg='#10b981', fg='white',
                padx=15, pady=8
            ).pack(side=tk.LEFT, padx=5, pady=3)
        
        self.current_gloss_label.config(text=f"✓ {len(glosses)} glosas - Reproduciendo...")
        
        # Auto-play
        self.play_videos()
    
    def play_videos(self):
        """Play videos automatically"""
        if not self.current_glosses or self.is_playing:
            return
        
        self.is_playing = True
        
        def play_bg():
            self.play_video_sequence()
            self.window.after(0, self.on_playback_finished)
        
        threading.Thread(target=play_bg, daemon=True).start()
    
    def play_video_sequence(self):
        """Play videos in right panel"""
        import cv2
        from PIL import Image, ImageTk
        import numpy as np
        
        for gloss in self.current_glosses:
            self.window.after(0, lambda g=gloss: self.current_gloss_label.config(text=f"▶️ {g}"))
            
            video_path = video_player.get_video_path(gloss)
            
            if video_path is None:
                self.show_text_placeholder(f"Video no disponible:\n{gloss}")
                time.sleep(2)
                continue
            
            # Play video
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                continue
            
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            delay = 1.0 / (fps * 0.8)
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert and resize
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize((640, 480), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                
                def update_frame(image=imgtk):
                    self.video_display.imgtk = image
                    self.video_display.configure(image=image, text="")
                
                self.window.after(0, update_frame)
                time.sleep(delay)
            
            cap.release()
            time.sleep(0.3)
    
    def show_text_placeholder(self, text):
        """Show placeholder"""
        import numpy as np
        from PIL import Image, ImageTk
        
        img_array = np.ones((480, 640, 3), dtype=np.uint8) * 30
        img = Image.fromarray(img_array)
        imgtk = ImageTk.PhotoImage(image=img)
        
        def update():
            self.video_display.imgtk = imgtk
            self.video_display.configure(image=imgtk, text=text, 
                                        compound=tk.CENTER, fg='white', font=("Segoe UI", 12))
        
        self.window.after(0, update)
    
    def on_playback_finished(self):
        """Playback done"""
        self.is_playing = False
        self.current_gloss_label.config(text=f"✓ Reproducción completa")
    
    def close_window(self):
        """Close"""
        self.window.destroy()
        self.on_close()
