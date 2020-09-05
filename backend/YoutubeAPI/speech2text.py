import datetime
import os

from google.cloud import speech_v1p1beta1
from google.cloud import storage

# bucket_name = 'audio-lezioni'
bucket_name = 'testinadimaiale'


class Speech2Text():

    def __init__(self, pathCredential: str) -> None:
        self.speech_client = speech_v1p1beta1.SpeechClient.from_service_account_json(pathCredential)
        self.storage_client = storage.Client.from_service_account_json(pathCredential)
        self.result = {}

    def create_bucket(self):
        """Creates a new bucket."""

        bucket = storage.Bucket(self.storage_client, name=bucket_name)

        bucket.location = "europe-west1"

        self.storage_client.create_bucket(bucket)

    def delete_blob(self, audioName: str):
        """Deletes a blob from the bucket."""

        bucket = storage.Bucket(self.storage_client, name=bucket_name)
        blob = bucket.blob(audioName)
        blob.delete()

        print("Blob {} deleted.".format(audioName))

    def upload_blob(self, audioName: str):
        """Uploads a file to the bucket."""

        destination_blob_name = audioName

        bucket = storage.Bucket(self.storage_client, name=bucket_name)
        blob = bucket.blob(destination_blob_name, chunk_size=2621440)

        blob.upload_from_filename('Audio/' + audioName)

        print(
            "File {} uploaded to {}.".format(
                audioName, destination_blob_name
            )
        )

    def sample_long_running_recognize(self, audioName: str):
        storage_uri = 'gs://' + bucket_name + '/' + audioName

        # The language of the supplied audio
        language_code = "it-IT"
        config = {
            "enable_word_time_offsets": True,
            "language_code": language_code,
            "enable_automatic_punctuation": True,
        }

        audio = {"uri": storage_uri}

        operation = self.speech_client.long_running_recognize(config, audio)

        response = operation.result()

        # The first result includes start and end time word offsets
        self.result = response.results
        return self.result

    def generateFile(self, directoryName):
        if os.path.exists('Outputs/' + directoryName + '/caption.txt'):
            os.remove('Outputs/' + directoryName + '/caption.txt')
        captionFile = open('Outputs/' + directoryName + '/caption.txt', 'a')

        if os.path.exists('Outputs/' + directoryName + '/text.txt'):
            os.remove('Outputs/' + directoryName + '/text.txt')
        textFile = open('Outputs/' + directoryName + '/text.txt', 'a')

        for sentence in self.result:
            alternative = sentence.alternatives[0]
            for word in alternative.words:
                if word.start_time.nanos:
                    captionFile.write(
                        word.word +
                        '<0' + str(datetime.timedelta(seconds=word.start_time.seconds,
                                                      milliseconds=word.start_time.nanos / 1000000))[:-3] + '> '
                    )
                else:
                    captionFile.write(
                        word.word +
                        '<0' + str(datetime.timedelta(seconds=word.start_time.seconds)) + '.' + '000' + '> ')
                textFile.write(word.word + ' ')
            captionFile.write('\r\n')
            textFile.write('\r\n')

        captionFile = open('Outputs/' + directoryName + '/caption.txt', 'r')
        return captionFile.read()
