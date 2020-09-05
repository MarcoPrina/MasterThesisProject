import moviepy.editor


class Video2audio():

    def processVideo(self, videoName):
        # Replace the parameter with the location of the video
        video = moviepy.editor.VideoFileClip('Video/' + videoName)
        audio = video.audio
        # Replace the parameter with the location along with filename
        audio.write_audiofile('Audio/' + videoName + ".flac", codec='flac', ffmpeg_params=["-ac", "1"])
