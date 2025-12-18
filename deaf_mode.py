"""
Deaf Mode Window with Advanced Controls
- Toggle preprocessing
- Toggle skeleton display
- Toggle TTS audio
- Collapsible glosses panel
- Camera selection
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import cv2
import numpy as np
import torch
import sys
from pathlib import Path
from PIL import Image, ImageTk

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from desktop_app.config import Config
from desktop_app.gemini_service import glosses_to_natural_text

# Import from realtime_inference.py
from sign_transfer_learning.realtime_inference import (
    create_holistic, create_hands, preprocess_frame_bgr,
    extract_landmarks_rgb, hands_present, draw_landmarks,
    normalize_spatial, pad_or_truncate, load_classes, build_model, load_checkpoint
)

# TTS
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("[TTS] pyttsx3 not available - audio disabled")


class DeafModeWindow:
    """Deaf Mode with preprocessing, skeleton, TTS toggles"""
    
    def __init__(self, parent_window, on_close_callback):
        self.parent = parent_window
        self.on_close = on_close_callback
        
        # Window
        self.window = tk.Toplevel(parent_window)
        self.window.title("Modo Sordo - Señas a Texto/Voz")
        self.window.geometry("1100x750")
        self.window.configure(bg='#0f172a')
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # State
        self.cap = None
        self.is_running = False
        self.camera_thread = None
        self.detected_glosses = []
        
        # Settings
        self.use_preprocessing = tk.BooleanVar(value=True)
        self.show_skeleton = tk.BooleanVar(value=True)
        self.enable_tts = tk.BooleanVar(value=False)
        self.glosses_visible = tk.BooleanVar(value=True)
        
        # TTS Engine
        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
        
        # Model state (will load async)
        self.model = None
        self.holistic = None
        self.hands_detector = None
        self.model_loaded = False
        
        # Create UI first (fast)
        self.create_ui()
        
        # Load model in background to avoid freezing
        self.load_model_async()
    
    def load_model(self):
        """Load model and MediaPipe"""
        print("[MODEL] Loading...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.classes = load_classes(Config.MODEL_DIR)
        n_feats = 75 * 3
        self.model = build_model(n_feats, len(self.classes), self.device)
        load_checkpoint(self.model, Config.MODEL_DIR, "best")
        self.holistic = create_holistic()
        self.hands_detector = create_hands()
        
        # FSM
        self.IDLE, self.RECORDING = 0, 1
        self.state = self.IDLE
        self.present_streak = 0
        self.absent_streak = 0
        self.seq_buffer = []
        print(f"[MODEL] Ready - {len(self.classes)} classes")
    
    def load_model_async(self):
        """Load model in background thread"""
        def load_in_background():
            self.load_model()
            self.model_loaded = True
            # Update UI when done
            try:
                if self.window.winfo_exists():
                    self.window.after(0, self.on_model_loaded)
            except tk.TclError:
                pass
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def on_model_loaded(self):
        """Called when model finishes loading"""
        try:
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(
                    text="✓ Modelo cargado - Presiona 'Iniciar' para comenzar",
                    fg='#10b981'
                )
            if hasattr(self, 'start_btn') and self.start_btn.winfo_exists():
                self.start_btn.config(state=tk.NORMAL)
        except tk.TclError:
            pass
    
    def create_ui(self):
        """Create UI with settings"""
        # Header - Modern style
        header = tk.Frame(self.window, bg='#1e293b', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="👋  Modo Sordo - Señas a Texto/Voz", 
                font=("Inter", 24, "bold"), bg='#1e293b', fg='#f8fafc').pack(pady=25)
        
        # Settings bar - Modern
        settings_frame = tk.Frame(self.window, bg='#0f172a')
        settings_frame.pack(fill=tk.X, padx=30, pady=(5, 15))
        
        settings_label = tk.Label(settings_frame, text="⚙️ Configuración:", 
                                  font=("Inter", 12, "bold"), bg='#0f172a', fg='#e0e7ff')
        settings_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Modern checkboxes with better styling
        tk.Checkbutton(settings_frame, text="  🔧 Preprocesamiento", variable=self.use_preprocessing,
                      bg='#0f172a', fg='#cbd5e1', selectcolor='#6366f1', 
                      activebackground='#0f172a', activeforeground='#f8fafc',
                      font=("Inter", 11), relief=tk.FLAT, bd=0).pack(side=tk.LEFT, padx=10)
        
        tk.Checkbutton(settings_frame, text="  🦴 Mostrar Esqueleto", variable=self.show_skeleton,
                      bg='#0f172a', fg='#cbd5e1', selectcolor='#6366f1',
           activebackground='#0f172a', activeforeground='#f8fafc',
                      font=("Inter", 11), relief=tk.FLAT, bd=0).pack(side=tk.LEFT, padx=10)
        
        tk.Checkbutton(settings_frame, text="  🔊 Reproducir Audio (TTS)", variable=self.enable_tts,
                      bg='#0f172a', fg='#cbd5e1', selectcolor='#10b981',
                      activebackground='#0f172a', activeforeground='#f8fafc',
                      font=("Inter", 11), relief=tk.FLAT, bd=0,
                      state=tk.NORMAL if TTS_AVAILABLE else tk.DISABLED).pack(side=tk.LEFT, padx=10)
        
        # Main content
        content = tk.Frame(self.window, bg='#0f172a')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # LEFT: Camera
        camera_frame = tk.Frame(content, bg='#1e293b')
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(camera_frame, text="📹 Cámara:", font=("Inter", 13, "bold"),
                bg='#1e293b', fg='#e0e7ff').pack(anchor=tk.W, padx=15, pady=(15, 8))
        
        self.camera_label = tk.Label(camera_frame, bg='#0f172a')
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Controls
        controls = tk.Frame(camera_frame, bg='#1e293b')
        controls.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.start_btn = tk.Button(controls, text="▶️  Iniciar", font=("Inter", 13, "bold"),
                                   bg='#10b981', fg='white', relief=tk.FLAT, cursor='hand2',
                                   command=self.start_camera, padx=20, pady=12,
                                   state=tk.DISABLED)  # Disabled until model loads
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        
        self.stop_btn = tk.Button(controls, text="⏹️  Detener", font=("Inter", 13, "bold"),
                                  bg='#ef4444', fg='white', relief=tk.FLAT, cursor='hand2',
                                  command=self.stop_camera, state=tk.DISABLED, padx=20, pady=12)
        self.stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 0))
        
        # RIGHT: Results
        results_frame = tk.Frame(content, bg='#1e293b', width=400)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        results_frame.pack_propagate(False)
        
        # Collapsible Glosses Section
        glosses_header = tk.Frame(results_frame, bg='#334155', cursor='hand2')
        glosses_header.pack(fill=tk.X, padx=10, pady=(10, 0))
        glosses_header.bind("<Button-1>", self.toggle_glosses)
        
        self.glosses_toggle_icon = tk.Label(glosses_header, text="▼", bg='#334155', fg='#cbd5e1',
                                            font=("Segoe UI", 10))
        self.glosses_toggle_icon.pack(side=tk.LEFT, padx=5, pady=5)
        self.glosses_toggle_icon.bind("<Button-1>", self.toggle_glosses)
        
        tk.Label(glosses_header, text="Señas Detectadas (click para ocultar/mostrar)",
                font=("Inter", 11, "bold"), bg='#334155', fg='#f8fafc').pack(side=tk.LEFT, pady=8)
        
        # Glosses content (collapsible)
        self.glosses_container = tk.Frame(results_frame, bg='#1e293b')
        self.glosses_container.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.glosses_text = scrolledtext.ScrolledText(self.glosses_container,
                                                      font=("Inter", 12, "bold"),
                                                      bg='#0f172a', fg='#818cf8',
                                                      height=6, wrap=tk.WORD, relief=tk.FLAT, padx=10, pady=8)
        self.glosses_text.pack(fill=tk.X, pady=8)
        self.glosses_text.config(state=tk.DISABLED)
        
        # Delete button below glosses
        delete_btn_frame = tk.Frame(self.glosses_container, bg='#1e293b')
        delete_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(
            delete_btn_frame,
            text="🗑️ Borrar Última Seña",
            font=("Inter", 10, "bold"),
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.delete_last_gloss,
            padx=15,
            pady=8
        ).pack()
        
        # Translation - Modern style
        tk.Label(results_frame, text="📝 Traducción:", font=("Inter", 13, "bold"),
                bg='#1e293b', fg='#e0e7ff').pack(anchor=tk.W, padx=15, pady=(15, 8))
        
        self.translation_text = scrolledtext.ScrolledText(results_frame,
                                                          font=("Inter", 13),
                                                          bg='#0f172a', fg='#f8fafc',
                                                          height=12, wrap=tk.WORD, relief=tk.FLAT, padx=12, pady=10)
        self.translation_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.translation_text.config(state=tk.DISABLED)
        
        # Controls
        ctrl = tk.Frame(results_frame, bg='#1e293b')
        ctrl.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(ctrl, text="ℹ️  Traducción automática al detener",
                font=("Inter", 10, "italic"), bg='#1e293b', fg='#94a3b8').pack(pady=5)
        
        tk.Button(ctrl, text="🗑️  Limpiar", font=("Inter", 11, "bold"),
                 bg='#475569', fg='white', relief=tk.FLAT, cursor='hand2',
                 command=self.clear_glosses, padx=20, pady=8).pack(pady=(8, 0))
        
        # Status
        self.status_label = tk.Label(results_frame, text="⏳ Cargando modelo...",
                                     font=("Segoe UI", 9), bg='#1e293b', fg='#f59e0b', wraplength=350)
        self.status_label.pack(padx=10, pady=(0, 10))
        
        # Back button - Modern and larger
        back_frame = tk.Frame(self.window, bg='#0f172a', height=70)
        back_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=30, pady=15)
        back_frame.pack_propagate(False)
        
        tk.Button(back_frame, text="←  Volver al Menú Principal", font=("Inter", 12, "bold"),
                 bg='#475569', fg='white', relief=tk.FLAT, cursor='hand2',
                 command=self.close_window, padx=30, pady=12).pack(expand=True)
    
    def toggle_glosses(self, event=None):
        """Toggle glosses panel visibility"""
        if self.glosses_visible.get():
            self.glosses_container.pack_forget()
            self.glosses_toggle_icon.config(text="▶")
            self.glosses_visible.set(False)
        else:
            self.glosses_container.pack(fill=tk.X, padx=10, pady=(0, 10), after=self.glosses_container.master.winfo_children()[0])
            self.glosses_toggle_icon.config(text="▼")
            self.glosses_visible.set(True)
    
    def start_camera(self):
        """Start camera"""
        # Check if model is loaded
        if not self.model_loaded:
            messagebox.showwarning("Modelo cargando", "Espera a que el modelo termine de cargar")
            return
        
        if self.is_running:
            return
        
        self.cap = cv2.VideoCapture(Config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
        
        # Critical: Set buffer size to 1 to avoid stale frames (matching behavior of realtime_inference.py with cv2.waitKey(1))
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo abrir la cámara")
            return
        
        # Reset
        self.state = self.IDLE
        self.present_streak = 0
        self.absent_streak = 0
        self.seq_buffer = []
        self.detected_glosses = []
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.is_running = True
        self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
        self.camera_thread.start()
    
    def stop_camera(self):
        """Stop and auto-translate"""
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.camera_label.config(image='')
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if self.detected_glosses:
            self.status_label.config(text="Traduciendo...", fg='#f59e0b')
            self.translate_glosses()
    
    def camera_loop(self):
        """Camera loop with conditional preprocessing and skeleton"""
        import time
        
        with torch.no_grad():
            while self.is_running and self.cap and self.cap.isOpened():
                start_time = time.time()
                ret, frame_bgr = self.cap.read()
                
                if not ret:
                    break
                
                # Conditional preprocessing
                if self.use_preprocessing.get():
                    frame_in = preprocess_frame_bgr(frame_bgr)
                else:
                    frame_in = frame_bgr.copy()
                
                frame_rgb = cv2.cvtColor(frame_in, cv2.COLOR_BGR2RGB)
                
                # Extract landmarks (with hands_detector fallback like realtime_inference.py)
                flat, res = extract_landmarks_rgb(frame_rgb, self.holistic, self.hands_detector)
                present = hands_present(res)
                
                # Conditional skeleton drawing
                if self.show_skeleton.get():
                    draw_landmarks(frame_bgr, res)
                
                # FSM
                self.process_fsm(flat, present)
                
                # Display
                self.display_frame(frame_bgr)
                
                # Small delay to prevent buffer buildup (similar to cv2.waitKey(1) in realtime_inference.py)
                elapsed = time.time() - start_time
                if elapsed < 0.001:  # minimum 1ms like cv2.waitKey(1)
                    time.sleep(0.001)
    
    def process_fsm(self, landmarks, present):
        """FSM logic"""
        if self.state == self.IDLE:
            self.absent_streak = 0
            self.present_streak = self.present_streak + 1 if present else 0
            
            if self.present_streak >= Config.START_STREAK:
                self.state = self.RECORDING
                self.seq_buffer = []
                self.present_streak = 0
        else:  # RECORDING
            self.seq_buffer.append(landmarks)
            self.present_streak = self.present_streak + 1 if present else 0
            self.absent_streak = self.absent_streak + 1 if not present else 0
            
            if (self.absent_streak >= Config.END_STREAK) or (len(self.seq_buffer) >= Config.MAX_SIGN_FRAMES):
                if len(self.seq_buffer) >= Config.MIN_SIGN_FRAMES:
                    self.classify_sequence()
                
                self.state = self.IDLE
                self.present_streak = 0
                self.absent_streak = 0
                self.seq_buffer = []
    
    def classify_sequence(self):
        """Classify"""
        seq = np.stack(self.seq_buffer, axis=0).astype(np.float32)
        seq = normalize_spatial(seq)
        seq = pad_or_truncate(seq, Config.MAX_LEN)
        
        x = torch.from_numpy(seq[None, ...]).to(self.device)
        lengths = torch.tensor([min(len(self.seq_buffer), Config.MAX_LEN)], device=self.device)
        logits = self.model(x, lengths=lengths)
        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        
        top_id = int(np.argmax(probs))
        conf = float(probs[top_id])
        gloss = self.classes[top_id]
        
        # Print with timestamp and segment info like realtime_inference.py
        import time as time_mod
        ts = time_mod.strftime("%H:%M:%S")
        seg_info = f"frames={len(self.seq_buffer)}"
        
        # Always add gloss (like realtime_inference.py), but show quality in print
        if conf >= Config.MIN_CONFIDENCE:
            print(f"[{ts}] {gloss} (p={conf:.3f}, {seg_info})", flush=True)
        else:
            print(f"[{ts}] {gloss} (p={conf:.3f}, {seg_info}) [LOW]", flush=True)
        
        self.add_detected_gloss(gloss)
    
    def delete_last_gloss(self):
        """Delete last detected gloss - simple button click"""
        if self.detected_glosses:
            deleted = self.detected_glosses.pop()
            print(f"[DELETE] Removed: {deleted}", flush=True)
            self.update_glosses_display()
    
    

    
    def add_detected_gloss(self, gloss):
        """Add gloss"""
        self.detected_glosses.append(gloss)
        self.window.after(0, self.update_glosses_display)
    
    def update_glosses_display(self):
        """Update glosses"""
        self.glosses_text.config(state=tk.NORMAL)
        self.glosses_text.delete("1.0", tk.END)
        self.glosses_text.insert("1.0", " ".join(self.detected_glosses))
        self.glosses_text.config(state=tk.DISABLED)
    
    def translate_glosses(self):
        """Translate with optional TTS"""
        if not self.detected_glosses:
            return
        
        def translate_bg():
            try:
                text = glosses_to_natural_text(self.detected_glosses)
                
                if text.startswith("Error") or "quota" in text.lower():
                    text = f"[No disponible] Glosas: {' '.join(self.detected_glosses)}"
                
                try:
                    if self.window.winfo_exists():
                        self.window.after(0, lambda: self.display_translation(text))
                        self.window.after(0, lambda: self.status_label.config(text="✓ Completado", fg='#10b981'))
                except tk.TclError:
                    pass
                
                # TTS
                if self.enable_tts.get() and TTS_AVAILABLE:
                    try:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    except:
                        pass
            except Exception as e:
                print(f"[ERROR] {e}", flush=True)
                fallback = f"[Error] Glosas: {' '.join(self.detected_glosses)}"
                try:
                    if self.window.winfo_exists():
                        self.window.after(0, lambda: self.display_translation(fallback))
                except:
                    pass
        
        threading.Thread(target=translate_bg, daemon=True).start()
    
    def display_translation(self, text):
        """Display translation"""
        try:
            if self.translation_text.winfo_exists():
                self.translation_text.config(state=tk.NORMAL)
                self.translation_text.delete("1.0", tk.END)
                self.translation_text.insert("1.0", text)
                self.translation_text.config(state=tk.DISABLED)
        except tk.TclError:
            pass  # Window already destroyed
    
    def clear_glosses(self):
        """Clear all"""
        self.detected_glosses = []
        
        self.glosses_text.config(state=tk.NORMAL)
        self.glosses_text.delete("1.0", tk.END)
        self.glosses_text.config(state=tk.DISABLED)
        
        self.translation_text.config(state=tk.NORMAL)
        self.translation_text.delete("1.0", tk.END)
        self.translation_text.config(state=tk.DISABLED)
        
        self.status_label.config(text="Limpiado", fg='#94a3b8')
    
    def display_frame(self, frame_bgr):
        """Display frame"""
        try:
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 360), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            
            def update():
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
            
            self.window.after(0, update)
        except:
            pass
    
    def close_window(self):
        """Close"""
        self.stop_camera()
        self.window.destroy()
        self.on_close()
