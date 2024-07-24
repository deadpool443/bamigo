from video_player import VideoPlayer
import vlc

class VideoControls:
    def __init__(self, video_path, loop=False,plugin_path=None):
        self.video_player = VideoPlayer(video_path,plugin_path=plugin_path)

    def start_video(self):
        self.video_player.play()

    def pause_video(self):
        self.video_player.pause()

    def stop_video(self):
        self.video_player.stop()

    def set_video_path(self, video_path):
        self.video_player._media = self.video_player._instance.media_new(video_path),
        self.video_player._player.set_media(self.video_player._media)
        self.video_player._video_path = video_path

        