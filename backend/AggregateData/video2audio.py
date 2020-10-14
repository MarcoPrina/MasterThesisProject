import moviepy.editor


class Video2audio():

    def processVideo(self, videoName):
        # Replace the parameter with the location of the video
        video = moviepy.editor.VideoFileClip(videoName)
        audio = video.audio

        audioName = videoName.replace("Video", "Audio", 1) + '.flac'
        audio.write_audiofile(audioName, codec='flac', ffmpeg_params=["-ac", "1"])
