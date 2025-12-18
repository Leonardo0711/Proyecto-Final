"""
SignBridge - Ultra Modern Glassmorphism Design
"""
import tkinter as tk
from tkinter import Canvas
from deaf_mode import DeafModeWindow
from hearing_mode import HearingModeWindow


class ModernCard(tk.Frame):
    """Modern card with glassmorphism effect"""
    
    def __init__(self, parent, title, subtitle, icon, color, command):
        super().__init__(parent, bg='#0f172a')
        self.command = command
        self.color = color
        self.is_hovered = False
        
        # Card container with shadow
        self.card = tk.Frame(self, bg=color, cursor='hand2')
        self.card.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Content
        content = tk.Frame(self.card, bg=color)
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=30)
        
        # Icon (large emoji)
        self.icon_label = tk.Label(
            content,
            text=icon,
            font=('Segoe UI Emoji', 60),
            bg=color,
            fg='white'
        )
        self.icon_label.pack(pady=(20, 15))
        
        # Title
        self.title_label = tk.Label(
            content,
            text=title,
            font=('Inter', 22, 'bold'),
            bg=color,
            fg='white'
        )
        self.title_label.pack(pady=(0, 8))
        
        # Subtitle with arrow
        self.subtitle_label = tk.Label(
            content,
            text=f"{subtitle} →",
            font=('Inter', 13),
            bg=color,
            fg='#e0e7ff'
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # Bind clicks to all widgets
        for widget in [self, self.card, content, self.icon_label, self.title_label, self.subtitle_label]:
            widget.bind('<Button-1>', lambda e: self.on_click())
            widget.bind('<Enter>', lambda e: self.on_enter())
            widget.bind('<Leave>', lambda e: self.on_leave())
    
    def on_enter(self):
        """Hover effect"""
        self.is_hovered = True
        lighter = self.lighten_color(self.color, 15)
        self.card.config(bg=lighter)
        for widget in [self.icon_label, self.title_label, self.subtitle_label]:
            widget.config(bg=lighter)
        self.config(cursor='hand2')
    
    def on_leave(self):
        """Leave hover"""
        self.is_hovered = False
        self.card.config(bg=self.color)
        for widget in [self.icon_label, self.title_label, self.subtitle_label]:
            widget.config(bg=self.color)
    
    def on_click(self):
        if self.command:
            self.command()
    
    def lighten_color(self, hex_color, amount):
        """Lighten hex color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
        return f'#{r:02x}{g:02x}{b:02x}'


class SignBridgeApp:
    """Modern glassmorphism UI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SignBridge")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)
        
        # Dark gradient background
        self.root.configure(bg='#0a0e1a')
        
        self.deaf_window = None
        self.hearing_window = None
        
        self.create_ui()
    
    def create_ui(self):
        """Create ultra-modern UI"""
        # Background gradient effect
        bg_canvas = tk.Canvas(self.root, bg='#0a0e1a', highlightthickness=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        def draw_bg():
            bg_canvas.delete('all')
            w = bg_canvas.winfo_width() or 1000
            h = bg_canvas.winfo_height() or 700
            
            # Dark gradient
            for i in range(h):
                ratio = i / h
                r = int(10 + (20 - 10) * ratio)
                g = int(14 + (25 - 14) * ratio)
                b = int(26 + (45 - 26) * ratio)
                color = f'#{r:02x}{g:02x}{b:02x}'
                bg_canvas.create_line(0, i, w, i, fill=color)
            
            # Decorative circles (glassmorphism style)
            bg_canvas.create_oval(w-250, -100, w+100, 250, 
                                 fill='#1e40af', outline='', stipple='gray50')
            bg_canvas.create_oval(-150, h-200, 150, h+100,
                                 fill='#7c3aed', outline='', stipple='gray50')
        
        bg_canvas.bind('<Configure>', lambda e: draw_bg())
        draw_bg()
        
        # Main container
        main = tk.Frame(self.root, bg='#0a0e1a')
        main.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.85, relheight=0.8)
        
        # Header with modern font
        header = tk.Frame(main, bg='#0a0e1a', height=150)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        # Logo/Title with gradient effect (simulated)
        title_frame = tk.Frame(header, bg='#0a0e1a')
        title_frame.pack(expand=True)
        
        tk.Label(
            title_frame,
            text="SignBridge",
            font=('Inter', 48, 'bold'),
            bg='#0a0e1a',
            fg='#f8fafc'
        ).pack()
        
        # Gradient line
        line_canvas = tk.Canvas(title_frame, height=4, bg='#0a0e1a', highlightthickness=0)
        line_canvas.pack(fill=tk.X, padx=200, pady=10)
        
        def draw_line():
            line_canvas.delete('all')
            w = line_canvas.winfo_width() or 200
            for i in range(w):
                ratio = i / w
                r = int(99 + (236 - 99) * ratio)
                g = int(102 + (72 - 102) * ratio)  
                b = int(241 + (153 - 241) * ratio)
                color = f'#{r:02x}{g:02x}{b:02x}'
                line_canvas.create_line(i, 0, i, 4, fill=color)
        
        line_canvas.bind('<Configure>', lambda e: draw_line())
        draw_line()
        
        tk.Label(
            title_frame,
            text="Traductor de Lengua de Señas Peruana",
            font=('Inter', 15),
            bg='#0a0e1a',
            fg='#94a3b8'
        ).pack(pady=(5, 0))
        
        # Subtitle with animation hint
        tk.Label(
            main,
            text="Selecciona un modo para comenzar ✨",
            font=('Inter', 16),
            bg='#0a0e1a',
            fg='#cbd5e1'
        ).pack(pady=(10, 40))
        
        # Cards container
        cards_container = tk.Frame(main, bg='#0a0e1a')
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        cards_container.grid_columnconfigure(0, weight=1)
        cards_container.grid_columnconfigure(1, weight=1)
        cards_container.grid_rowconfigure(0, weight=1)
        
        # Deaf Mode Card - Purple/Blue gradient
        deaf_card = ModernCard(
            cards_container,
            title="Modo Sordo",
            subtitle="Señas → Texto/Voz",
            icon="👋",
            color='#6366f1',  # Indigo
            command=self.open_deaf_mode
        )
        deaf_card.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
        
        # Hearing Mode Card - Green/Teal gradient  
        hearing_card = ModernCard(
            cards_container,
            title="Modo Oyente",
            subtitle="Texto → Señas",
            icon="🗣️",
            color='#10b981',  # Emerald
            command=self.open_hearing_mode
        )
        hearing_card.grid(row=0, column=1, sticky='nsew', padx=(15, 0))
        
        # Footer
        footer = tk.Frame(self.root, bg='#0a0e1a', height=50)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        footer.pack_propagate(False)
        
        tk.Label(
            footer,
            text="© 2024 SignBridge • Desarrollado para LSP",
            font=('Inter', 10),
            bg='#0a0e1a',
            fg='#475569'
        ).pack(pady=15)
    
    def open_deaf_mode(self):
        if self.deaf_window is None:
            self.deaf_window = DeafModeWindow(
                self.root,
                on_close_callback=lambda: setattr(self, 'deaf_window', None)
            )
    
    def open_hearing_mode(self):
        if self.hearing_window is None:
            self.hearing_window = HearingModeWindow(
                self.root,
                on_close_callback=lambda: setattr(self, 'hearing_window', None)
            )


def main():
    root = tk.Tk()
    
    # Try to use Inter font (fallback to Segoe UI)
    try:
        import matplotlib.font_manager as fm
    except:
        pass
    
    app = SignBridgeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
