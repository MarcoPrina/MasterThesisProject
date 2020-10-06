class CropCaption():

    def __init__(self, videoID: str) -> None:
        self.videoID = videoID

    def getUsableCaption(self) -> str:
        with open('Media/YoutubeCaptions/' + self.videoID + '.vtt') as f:
            temp_final = f.read().replace('\n', "\r\n").replace('"', "'")

            caption = self.remove_duplicate_lines(temp_final)

        return caption

    def remove_duplicate_lines(self, temp_final: str) -> str:
        final = ''
        for line in temp_final.split("\r\n"):
            if line.__contains__('<c>'):
                final += line.replace('<c>', '').replace('</c>', '') + "\r\n"

        return final
