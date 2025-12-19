# SignBridge Desktop App - Guía Completa

Aplicación de escritorio profesional para traducción bidireccional de Lengua de Señas Peruana.

## 🎯 Características

### 👋 Modo Sordo (Señas → Texto/Voz)
- ✅ Detección de señas con OpenCV + MediaPipe (960x540)
- ✅ Modelo PyTorch pre-entrenado
- ✅ Toggle preprocesamiento (gamma + CLAHE + bilateral)
- ✅ Toggle mostrar esqueleto MediaPipe
- ✅ Toggle reproducción de audio (TTS)
- ✅ Panel de glosas colapsable
- ✅ Traducción automática al detener cámara
- ✅ Traducción

### 🗣️ Modo Oyente (Texto/Voz → Señas)
- ✅ Entrada de texto manual
- ✅ **Dictado por voz** (Speech Recognition)
- ✅ Traducción a glosas 
- ✅ Reproducción automática de videos
- ✅ Videos integrados en interfaz (no ventanas externas)
- ✅ Layout responsive de 2 columnas

## 📦 Instalación

```bash
# 1. Navegar a la carpeta
cd desktop_app

# 2. Activar entorno (Python 3.10+)
conda activate lsp310

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar PyAudio (Windows)
# Descargar wheel desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Ejemplo para Python 3.10, 64-bit:
pip install PyAudio-0.2.13-cp310-cp310-win_amd64.whl
```

## ⚙️ Configuración

Editar `.env` con tus rutas:

```env
GEMINI_API_KEY=tu_api_key_aqui
PROJECT_ROOT=d:/UNI/25-2/Tesis/Proyecto_Tesis
VIDEOS_DIR=d:/UNI/25-2/Tesis/Proyecto_Tesis/videos
GLOSA_INDEX_PATH=d:/UNI/25-2/Tesis/Proyecto_Tesis/videos/glosa_index.json
MODEL_DIR=d:/UNI/25-2/Tesis/Proyecto_Tesis/models_lsp
CAMERA_INDEX=0
FRAME_WIDTH=960
FRAME_HEIGHT=540
```

## 🚀 Uso

```bash
python main.py
```

### Modo Sordo
1. Click "Modo Sordo"
2. Configurar opciones (preprocesamiento, esqueleto, audio)
3. "Iniciar Cámara"
4. Hacer señas frente a la cámara
5. "Detener" → Traducción automática
6. (Opcional) Audio TTS si está activado

### Modo Oyente
1. Click "Modo Oyente"
2. **Escribir** texto O **Dictar** con 🎤
3. Click "Traducir a Señas"
4. Videos se reproducen automáticamente en panel derecho

## 🎨 Características UI

- ✨ Diseño moderno con gradientes
- 🌙 Tema oscuro (dark mode)
- 📱 Layout responsive
- 🎭 Animaciones suaves
- 🖼️ Iconos emoji intuitivos
- 🔧 Controles colapsables

## 🔧 Controles Modo Sordo

| Control | Función |
|---------|---------|
| 🔧 Preprocesamiento | Gamma + CLAHE + Bilateral Filter |
| 🦴 Esqueleto | Dibuja landmarks MediaPipe |
| 🔊 Audio (TTS) | Lee traducción en voz alta |
| Click header glosas | Colapsar/expandir panel de glosas |

## 🎤 Dictado por Voz

Requiere micrófono funcional:
1. Click "🎤 Dictar por Voz"
2. Esperar señal "Escuchando..."
3. Hablar claramente en español
4. Texto aparece en campo automáticamente

## 📊 Ventajas vs Web App

| Aspecto | Web App | Desktop App |
|---------|---------|-------------|
| Cámara | WebRTC (variable) | OpenCV directo ✅ |
| Precisión | Afectada por red | **Idéntica a `.bat`** ✅ |
| Latencia | ~100-300ms (HTTP) | ~0ms (local) ✅ |
| Compresión | JPEG base64 | Sin compresión ✅ |
| Resolución | Browser-dependent | Controlada 960x540 ✅ |
| FSM | Igual | Igual ✅ |
| UI | Hermosa | **Hermosa + Responsive** ✅ |

## 📁 Estructura

```
desktop_app/
├── main.py              # Menu principal
├── deaf_mode.py         # Señas → Texto/Voz  
├── hearing_mode.py      # Texto/Voz → Señas
├── gemini_service.py    # Gemini API (nueva)
├── video_player.py      # Reproductor de videos
├── config.py            # Configuración
├── .env                 # Variables de entorno
├── requirements.txt     # Dependencias
└── README.md           # Esta guía
```

## 🐛 Troubleshooting

### PyAudio no instala
```bash
# Windows: Descargar wheel precompilado
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio-XXXXX.whl
```

### Micrófono no funciona
- Verificar permisos de Windows
- Probar con `python -m speech_recognition`

### Cámara no abre
- Verificar `CAMERA_INDEX` en `.env`
- Probar con diferentes valores (0, 1, 2...)

### Videos no reproducen
- Verificar rutas en `.env`
- Verificar `glosa_index.json` existe
- Verificar videos en formato MP4 H.264

## 🔮 Próximas Mejoras

- [ ] Historial de traducciones
- [ ] Exportar a PDF
- [ ] Modo práctica/entrenamiento
- [ ] Estadísticas de uso
- [ ] Soporte multi-idioma

## 👨‍💻 Desarrollo

Desarrollado para tesis de traducción LSP.
Tecnologías: Python, Tkinter, OpenCV, MediaPipe, PyTorch, Gemini AI

---

**Versión**: 1.0.0  
**Última actualización**: Diciembre 2024
