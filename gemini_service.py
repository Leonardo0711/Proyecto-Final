"""
Gemini API Service with Multi-Model Fallback
Tries multiple models in cascade: 1.5-flash → 2.5-flash-lite → 2.5-flash → local
"""
from google import genai
from google.genai import types
from typing import List
import time
from desktop_app.config import Config


# Client auto-detects GEMINI_API_KEY from environment
client = genai.Client(api_key=Config.GEMINI_API_KEY)

# Model cascade - try in this order
MODELS = [
    "gemini-1.5-flash",        # Best limits: 15 RPM, 1M tokens/day
    "gemini-2.5-flash-lite",   # Good limits: 10 RPM, 250K tokens/day  
    "gemini-2.5-flash",        # Lower limits: ~2 RPD, but high quality
]

print(f"[GEMINI] Cliente inicializado con {len(MODELS)} modelos en cascada", flush=True)


def try_models(prompt: str, max_tokens: int = 100) -> str:
    """Try models in cascade until one works"""
    
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    temperature=0.7,
                    max_output_tokens=max_tokens
                )
            )
            
            result = response.text.strip()
            print(f"[GEMINI] ✓ {model} funcionó", flush=True)
            return result
            
        except Exception as e:
            error_str = str(e)
            
            # Check if quota/rate limit error
            if '429' in error_str or 'quota' in error_str.lower() or 'RESOURCE_EXHAUSTED' in error_str:
                print(f"[GEMINI] ⚠️ {model} agotado - probando siguiente...", flush=True)
                continue
            else:
                # Other error - also try next model
                print(f"[GEMINI] ⚠️ {model} error: {error_str[:100]}", flush=True)
                continue
    
    # All models failed
    print(f"[GEMINI] ✗ Todos los modelos agotados - usando fallback local", flush=True)
    return None


def glosses_to_natural_text(glosses: List[str]) -> str:
    """
    Convert LSP glosses to natural Spanish text
    Tries multiple Gemini models in cascade
    """
    if not glosses:
        return ""
    
    glosses_str = " ".join(glosses)
    
    prompt = f"""Convierte estas glosas de Lengua de Señas Peruana (LSP) a español natural.

REGLAS LSP:
1. Letras individuales (A, B, C, etc.) = deletreo de nombres propios
2. Verbos están en infinitivo: QUERER, IR, TENER, SER, etc.
3. Sustantivos en singular: CASA, PERRO, LIBRO
4. Sin artículos: "LA CASA" se escribe solo "CASA"

Glosas: {glosses_str}

Responde SOLO la traducción en español natural, sin explicaciones:"""
    
    print(f"[GEMINI] Traduciendo: {glosses_str}", flush=True)
    
    # Try models in cascade
    result = try_models(prompt, max_tokens=100)
    
    if result:
        print(f"[GEMINI] ✓ Resultado: {result}", flush=True)
        return result
    
    # Fallback: basic local processing
    result = " ".join(glosses).replace("_", " ").lower()
    if result:
        result = result[0].upper() + result[1:]
    print(f"[GEMINI] Fallback local: {result}", flush=True)
    return result


def natural_text_to_glosses(text: str) -> List[str]:
    """
    Convert natural Spanish text to LSP glosses
    Tries multiple Gemini models in cascade
    """
    if not text or not text.strip():
        return []
    
    prompt = f"""Convierte este texto en español a glosas de Lengua de Señas Peruana (LSP).

REGLAS:
1. Verbos en INFINITIVO y MAYÚSCULAS: "quiero" → QUERER, "tengo" → TENER
2. Sustantivos en SINGULAR: "casas" → CASA
3. SIN artículos (el, la, los, las, un, una)
4. SIN preposiciones innecesarias (de, del, a, en)
5. Nombres propios DELETREAR: "Leo" → L E O
6. Orden puede cambiar para claridad gestual

Texto: {text}

Responde SOLO las glosas separadas por espacios, en MAYÚSCULAS:"""
    
    print(f"[GEMINI] Convirtiendo: {text}", flush=True)
    
    # Try models in cascade
    result = try_models(prompt, max_tokens=50)
    
    if result:
        glosses = [g.strip().upper() for g in result.split() if g.strip()]
        print(f"[GEMINI] ✓ Glosas: {glosses}", flush=True)
        return glosses
    
    # Fallback: simple local processing
    import re
    text_clean = re.sub(r'[¿?¡!.,;:]', '', text.lower())
    
    # Common Spanish stop words
    stop_words = {
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'de', 'del', 'al', 'a', 'en', 'por', 'para', 'con', 'sin',
        'y', 'o', 'pero', 'si', 'no', 'que', 'como', 'cuando',
        'me', 'te', 'se', 'le', 'lo', 'mi', 'tu', 'su', 'es', 'son'
    }
    
    words = [w.upper() for w in text_clean.split() if w not in stop_words and len(w) > 1]
    result = words if words else [text.upper()]
    
    print(f"[GEMINI] Fallback local: {result}", flush=True)
    return result
