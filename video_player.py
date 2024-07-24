import vlc
import logging
import time
import os
import sys
import ctypes

class VideoPlayer:
    def __init__(self, video_path, plugin_path=None):
        logging.info(f"Initializing VideoPlayer with video path: {video_path}")
        
        if not os.path.exists(video_path):
            logging.error(f"Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            logging.info(f"Python version: {sys.version}")
            logging.info(f"VLC module version: {vlc.__version__}")
            logging.info(f"VLC module path: {vlc.__file__}")

            if sys.platform.startswith('win'):
                if plugin_path:
                    os.environ['VLC_PLUGIN_PATH'] = plugin_path
                else:
                    plugin_path = 'C:\\Program Files\\VideoLAN\\VLC\\plugins'
                    os.environ['VLC_PLUGIN_PATH'] = plugin_path
                logging.info(f"Set VLC_PLUGIN_PATH to: {plugin_path}")
                
                vlc_path = 'C:\\Program Files\\VideoLAN\\VLC\\libvlc.dll'
                if os.path.exists(vlc_path):
                    ctypes.CDLL(vlc_path)
                    logging.info(f"Loaded VLC library from: {vlc_path}")
                else:
                    logging.error(f"VLC library not found at: {vlc_path}")
                    raise FileNotFoundError(f"VLC library not found at: {vlc_path}")

            self._instance = vlc.Instance('--verbose=2')
            if self._instance is None:
                raise RuntimeError("Failed to create VLC instance")
            logging.info("VLC instance created successfully")
            logging.info(f"VLC version: {vlc.libvlc_get_version().decode()}")

            self._player = self._instance.media_player_new()
            if self._player is None:
                raise RuntimeError("Failed to create media player")
            logging.info("Media player created successfully")

            self._media = self._instance.media_new(video_path)
            if self._media is None:
                raise RuntimeError("Failed to create media")
            logging.info("Media created successfully")

            self._player.set_media(self._media)
            logging.info("Media set to player successfully")

        except Exception as e:
            logging.error(f"Error initializing VLC: {e}")
            logging.info(f"VLC plugin path: {os.environ.get('VLC_PLUGIN_PATH', 'Not set')}")
            logging.info(f"System PATH: {os.environ.get('PATH', '')}")
            raise

        logging.info("Video player initialization complete")

    def play(self):
        if self._player.play() == -1:
            logging.error("Failed to play the media")
        else:
            logging.info("Media playback started")

    def pause(self):
        self._player.pause()
        logging.info("Media playback paused")

    def stop(self):
        self._player.stop()
        logging.info("Media playback stopped")