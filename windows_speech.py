"""
Windows Speech Recognition using native SAPI
No FLAC required!
"""
import threading
import queue

try:
    import win32com.client
    WINDOWS_SR_AVAILABLE = True
except ImportError:
    WINDOWS_SR_AVAILABLE = False


class WindowsSpeechRecognizer:
    """Windows native speech recognition using SAPI"""
    
    def __init__(self):
        if not WINDOWS_SR_AVAILABLE:
            raise ImportError("pywin32 not available")
        
        self.listener = None
        self.context = None
        self.grammar = None
        self.result_queue = queue.Queue()
        self.is_listening = False
    
    def listen_once(self, timeout=5, language='es-ES'):
        """
        Listen for speech once and return recognized text
        
        Args:
            timeout: Maximum seconds to wait
            language: Language code (es-ES for Spanish)
            
        Returns:
            Recognized text or None if timeout/error
        """
        try:
            # Create speech recognizer
            recognizer = win32com.client.Dispatch("SAPI.SpInProcRecoContext")
            
            # Set to dictation grammar (free-form speech)
            grammar = recognizer.CreateGrammary(0)
            grammar.DictationSetState(1)  # Enable dictation
            
            # Event handler for recognition
            class SpeechEvents:
                def __init__(self, result_queue):
                    self.queue = result_queue
                
                def OnRecognition(self, StreamNumber, StreamPosition, RecognitionType, Result):
                    text = Result.PhraseInfo.GetText()
                    self.queue.put(text)
            
            # Connect events
            event_handler = SpeechEvents(self.result_queue)
            recognizer = win32com.client.DispatchWithEvents(
                "SAPI.SpInProcRecoContext",
                SpeechEvents
            )
            
            # Wait for result
            try:
                result = self.result_queue.get(timeout=timeout)
                return result
            except queue.Empty:
                return None
                
        except Exception as e:
            print(f"[SAPI] Error: {e}")
            return None
    
    def cleanup(self):
        """Cleanup resources"""
        if self.grammar:
            try:
                self.grammar.DictationSetState(0)
            except:
                pass


# Simplified interface matching SpeechRecognition
class Microphone:
    """Dummy microphone class for compatibility"""
    pass


class Recognizer:
    """Windows SAPI recognizer"""
    
    def __init__(self):
        self.windows_sr = WindowsSpeechRecognizer() if WINDOWS_SR_AVAILABLE else None
    
    def recognize_google(self, audio, language='es-ES'):
        """Dummy - not used with Windows SR"""
        raise NotImplementedError("Use listen() instead")
    
    def listen(self, source, timeout=5, phrase_time_limit=10):
        """Listen using Windows SAPI"""
        return None  # Placeholder
    
    def adjust_for_ambient_noise(self, source, duration=1):
        """Dummy for compatibility"""
        pass


# Test if Windows SR is available
def test_windows_sr():
    """Test if Windows Speech Recognition works"""
    try:
        recognizer = win32com.client.Dispatch("SAPI.SpVoice")
        recognizer.Speak("Test")
        return True
    except:
        return False
