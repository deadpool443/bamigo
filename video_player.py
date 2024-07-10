import vlc
import logging
import time
import os


class VideoPlayer:
    def __init__(self, video_path):
        # ...
        vlc_options = [
            '--no-video-title-show',
            '--quiet',
            '--fullscreen',
            f'--plugin-path=C:\\Program Files\\VideoLAN\\VLC'
        ]
        
        self._instance = vlc.Instance(' '.join(vlc_options))
        self._player = self._instance.media_player_new()
        
        self._media_list = self._instance.media_list_new([video_path])
        self._list_player = self._instance.media_list_player_new()
        self._list_player.set_media_player(self._player)
        self._list_player.set_media_list(self._media_list)
        
        self._list_player.set_playback_mode(vlc.PlaybackMode.loop)

    def play(self):
        try:
            self._list_player.play()
            logging.info("Video playback started/resumed.")
            time.sleep(1)
            self._player.set_fullscreen(True)
            logging.info("Fullscreen mode activated.")
            time.sleep(1)
            if not self._player.get_fullscreen():
                self._player.set_fullscreen(True)
                logging.info("Fullscreen mode re-activated after checking.")
            else:
                logging.info("Confirmed player remains in fullscreen mode.")
        except Exception as e:
            logging.error(f"Error during video playback: {str(e)}")
    
    def pause(self):
        try:
            self._list_player.pause()
            logging.info("Video playback paused.")
        except Exception as e:
            logging.error(f"Error while pausing video: {str(e)}")

    def stop(self):
        try:
            self._list_player.stop()
            self._player.set_fullscreen(False)
            logging.info("Video playback stopped.")
        except Exception as e:
            logging.error(f"Error while stopping video: {str(e)}")
