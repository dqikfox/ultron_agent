"""
Comprehensive tests for Voice Manager system
"""
import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from voice_manager import UltronVoiceManager


class TestUltronVoiceManager:
    """Test suite for UltronVoiceManager"""

    def test_voice_manager_initialization_with_config(self):
        """Test voice manager initialization with config"""
        mock_config = Mock()
        mock_config.get.return_value = "pyttsx3"
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'):
            manager = UltronVoiceManager(config=mock_config)
            assert manager.config == mock_config

    def test_voice_manager_initialization_without_config(self):
        """Test voice manager initialization without config"""
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('config.Config') as mock_config_class:
            manager = UltronVoiceManager()
            mock_config_class.assert_called_once()

    @patch('pyttsx3.init')
    def test_initialize_engines_success(self, mock_pyttsx3_init):
        """Test successful engine initialization"""
        mock_config = Mock()
        mock_config.get.return_value = "pyttsx3"
        mock_engine = Mock()
        mock_pyttsx3_init.return_value = mock_engine
        
        manager = UltronVoiceManager(config=mock_config)
        
        assert 'pyttsx3' in manager.engines
        assert manager.engines['pyttsx3'] == mock_engine

    @patch('pyttsx3.init')
    def test_initialize_engines_failure(self, mock_pyttsx3_init):
        """Test engine initialization failure handling"""
        mock_config = Mock()
        mock_config.get.return_value = "pyttsx3"
        mock_pyttsx3_init.side_effect = Exception("Engine failed")
        
        manager = UltronVoiceManager(config=mock_config)
        
        # Should handle failure gracefully
        assert 'pyttsx3' not in manager.engines or manager.engines['pyttsx3'] is None

    def test_speak_async_mode(self):
        """Test speaking in async mode"""
        mock_config = Mock()
        mock_config.get.return_value = "pyttsx3"
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('voice_manager.UltronVoiceManager._speak_async') as mock_speak_async:
            manager = UltronVoiceManager(config=mock_config)
            manager.speak("test message", async_mode=True)
            mock_speak_async.assert_called_once_with("test message")

    def test_speak_sync_mode(self):
        """Test speaking in sync mode"""
        mock_config = Mock()
        mock_config.get.return_value = "pyttsx3"
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('voice_manager.UltronVoiceManager._speak_sync') as mock_speak_sync:
            manager = UltronVoiceManager(config=mock_config)
            manager.speak("test message", async_mode=False)
            mock_speak_sync.assert_called_once_with("test message")

    def test_speak_engine_fallback(self):
        """Test engine fallback when primary engine fails"""
        mock_config = Mock()
        mock_config.get.return_value = "enhanced"
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('voice_manager.UltronVoiceManager._try_engine') as mock_try_engine:
            
            # First engine fails, second succeeds
            mock_try_engine.side_effect = [False, True, False]
            
            manager = UltronVoiceManager(config=mock_config)
            manager._speak_sync("test message")
            
            # Should try multiple engines
            assert mock_try_engine.call_count >= 2

    def test_try_engine_pyttsx3_success(self):
        """Test successful pyttsx3 engine usage"""
        mock_config = Mock()
        mock_engine = Mock()
        
        manager = UltronVoiceManager(config=mock_config)
        manager.engines = {'pyttsx3': mock_engine}
        
        result = manager._try_engine('pyttsx3', "test message")
        
        mock_engine.say.assert_called_once_with("test message")
        mock_engine.runAndWait.assert_called_once()
        assert result is True

    def test_try_engine_pyttsx3_failure(self):
        """Test pyttsx3 engine failure handling"""
        mock_config = Mock()
        mock_engine = Mock()
        mock_engine.say.side_effect = Exception("Engine error")
        
        manager = UltronVoiceManager(config=mock_config)
        manager.engines = {'pyttsx3': mock_engine}
        
        result = manager._try_engine('pyttsx3', "test message")
        assert result is False

    @patch('requests.post')
    def test_speak_openai_success(self, mock_post):
        """Test OpenAI TTS success"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            'openai_api_key': 'test_key'
        }.get(key, default)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"audio_data"
        mock_post.return_value = mock_response
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('tempfile.NamedTemporaryFile') as mock_temp, \
             patch('pygame.mixer.init'), \
             patch('pygame.mixer.music.load'), \
             patch('pygame.mixer.music.play'), \
             patch('pygame.mixer.music.get_busy', return_value=False):
            
            mock_temp_file = Mock()
            mock_temp_file.name = "temp_audio.mp3"
            mock_temp.return_value.__enter__.return_value = mock_temp_file
            
            manager = UltronVoiceManager(config=mock_config)
            result = manager._speak_openai("test message")
            
            assert result is True

    @patch('requests.post')
    def test_speak_openai_failure(self, mock_post):
        """Test OpenAI TTS failure"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda key, default=None: {
            'openai_api_key': 'test_key'
        }.get(key, default)
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'):
            manager = UltronVoiceManager(config=mock_config)
            result = manager._speak_openai("test message")
            
            assert result is False

    def test_speak_openai_no_api_key(self):
        """Test OpenAI TTS without API key"""
        mock_config = Mock()
        mock_config.get.return_value = None
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'):
            manager = UltronVoiceManager(config=mock_config)
            result = manager._speak_openai("test message")
            
            assert result is False

    def test_voice_worker_thread(self):
        """Test voice worker thread functionality"""
        mock_config = Mock()
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'):
            manager = UltronVoiceManager(config=mock_config)
            manager.voice_queue = Mock()
            manager.voice_queue.get.side_effect = ["test message", None]  # Second call should exit
            
            with patch('voice_manager.UltronVoiceManager._speak_sync') as mock_speak:
                manager._voice_worker()
                mock_speak.assert_called_once_with("test message")

    def test_start_voice_worker(self):
        """Test starting voice worker thread"""
        mock_config = Mock()
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('threading.Thread') as mock_thread:
            manager = UltronVoiceManager(config=mock_config)
            manager._start_voice_worker()
            
            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()

    def test_shutdown(self):
        """Test voice manager shutdown"""
        mock_config = Mock()
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'):
            manager = UltronVoiceManager(config=mock_config)
            manager.voice_queue = Mock()
            manager.worker_thread = Mock()
            manager.worker_thread.is_alive.return_value = True
            
            manager.shutdown()
            
            manager.voice_queue.put.assert_called_with(None)
            manager.worker_thread.join.assert_called_once()

    def test_test_voice_functionality(self):
        """Test voice testing functionality"""
        mock_config = Mock()
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('voice_manager.UltronVoiceManager.speak') as mock_speak:
            manager = UltronVoiceManager(config=mock_config)
            manager.test_voice()
            
            mock_speak.assert_called_once()

    def test_get_voice_manager_singleton(self):
        """Test voice manager singleton pattern"""
        mock_config = Mock()
        
        with patch('voice_manager.UltronVoiceManager') as mock_manager_class:
            mock_instance = Mock()
            mock_manager_class.return_value = mock_instance
            
            from voice_manager import get_voice_manager
            
            # First call should create instance
            result1 = get_voice_manager(mock_config)
            # Second call should return same instance
            result2 = get_voice_manager(mock_config)
            
            assert result1 == result2
            mock_manager_class.assert_called_once()

    def test_test_voice_system_function(self):
        """Test standalone test voice system function"""
        with patch('voice_manager.get_voice_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            from voice_manager import test_voice_system
            test_voice_system()
            
            mock_manager.test_voice.assert_called_once()

    @patch('queue.Queue')
    def test_async_speak_queuing(self, mock_queue_class):
        """Test async speak message queuing"""
        mock_config = Mock()
        mock_queue = Mock()
        mock_queue_class.return_value = mock_queue
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('voice_manager.UltronVoiceManager._start_voice_worker'):
            manager = UltronVoiceManager(config=mock_config)
            manager.voice_queue = mock_queue
            
            manager._speak_async("test message")
            mock_queue.put.assert_called_once_with("test message")

    def test_engine_preference_order(self):
        """Test engine preference and fallback order"""
        mock_config = Mock()
        mock_config.get.return_value = "enhanced"
        
        with patch('voice_manager.UltronVoiceManager._initialize_engines'), \
             patch('voice_manager.UltronVoiceManager._try_engine') as mock_try_engine:
            
            # All engines fail except console
            mock_try_engine.return_value = False
            
            manager = UltronVoiceManager(config=mock_config)
            manager._speak_sync("test message")
            
            # Should try engines in preference order
            expected_engines = ['enhanced', 'pyttsx3', 'openai', 'console']
            call_args = [call[0][0] for call in mock_try_engine.call_args_list]
            
            # Verify engines are tried in correct order
            for i, engine in enumerate(expected_engines):
                if i < len(call_args):
                    assert call_args[i] == engine
