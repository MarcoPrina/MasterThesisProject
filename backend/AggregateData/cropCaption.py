class CropCaption():

    def __init__(self, directoryName: str, captionFileName='caption.vtt') -> None:
        self.captionFileName = captionFileName
        self.directoryName = directoryName
        self.caption = ''

    def getUsableCaption(self) -> str:
        with open('Outputs/' + self.directoryName + '/' + self.captionFileName) as f:
            temp_final = f.read().replace('\n', "\r\n").replace('"', "'")

            self.caption = self.remove_duplicate_lines(temp_final)

        return self.caption

    def remove_duplicate_lines(self, temp_final: str) -> str:
        final = ''
        for line in temp_final.split("\r\n"):
            if line.__contains__('<c>'):
                final += line.replace('<c>', '').replace('</c>', '') + "\r\n"

        return final

    def generateFile(self, fileName='caption'):
        text_file = open('Outputs/' + self.directoryName + "/" + fileName + ".txt", "w")

        text_file.write(self.caption)

        text_file.close()
