from collections import defaultdict

from backend.models import Word, WordCountForLesson


class FindWords():

    def __init__(self) -> None:
        self.ordered = []
        self.words = []

    def search(self, tokenizedCaptions, posTag=['']) -> list:
        words = {}
        totWords = 0
        for token in tokenizedCaptions:
            totWords += 1
            if token['pos'].startswith(tuple(posTag)):

                self.words.append({
                    'word': token['word'][:-1].lower(),
                    'time_stamp': token['time']
                })

                if token['word'][:-1].lower() in words:
                    words[token['word'][:-1].lower()]['counter'] += 1
                    words[token['word'][:-1].lower()]['pos'][token['pos']] += 1
                else:
                    words[token['word'][:-1].lower()] = {}
                    words[token['word'][:-1].lower()]['counter'] = 1
                    words[token['word'][:-1].lower()]['word'] = token['word'].lower()
                    words[token['word'][:-1].lower()]['pos'] = defaultdict(int)
                    words[token['word'][:-1].lower()]['pos'][token['pos']] += 1

        for word in words:
            words[word]['tf'] = words[word]['counter'] / totWords
        self.ordered = sorted(words.items(), key=lambda x: x[1]['counter'], reverse=True)
        return self.ordered

    def saveOnDB(self, lezione):
        Word.objects.filter(lezione=lezione).delete()
        WordCountForLesson.objects.filter(lezione=lezione).delete()

        for word in self.words:
            wor = Word(word=word['word'], time_stamp=word["time_stamp"], lezione=lezione)
            wor.save()

        for word, data in self.ordered:
            wor = WordCountForLesson(word=word, count=data['counter'], lezione=lezione, tf=data['tf'])
            wor.save()
