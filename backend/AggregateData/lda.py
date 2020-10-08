import gensim
from gensim import corpora
from gensim.models import CoherenceModel

from backend.models import LdaTopic, LdaWord


class LDA():

    def __init__(self):
        self.mallet_path = 'mallet-2.0.8/mallet-2.0.8/bin/mallet'

    def findTopic(self, tokens, posTag=[''], nTopic=5):
        buffTokens = []
        ldaTokens = []
        for num, token in enumerate(tokens):
            if token['pos'].startswith(tuple(posTag)) and len(token['word']) > 2:
                buffTokens.append(token['word'][:-1])
            if '.' or '?' or '!' in token['word']:
                ldaTokens.append(buffTokens)
                buffTokens = []

        ldaTokens.append(buffTokens)

        dictionary = corpora.Dictionary(ldaTokens)
        corpus = [dictionary.doc2bow(text) for text in ldaTokens]

        # self.ldamodel = gensim.models.ldamodel.LdaModel(self.corpus, num_topics=nTopic, id2word=self.dictionary, passes=15)

        self.ldamodel = gensim.models.wrappers.LdaMallet(self.mallet_path, corpus=corpus, num_topics=nTopic, id2word=dictionary)

        # self.ldamodel.save('model5.gensim')

        # Compute Perplexity
        #print('\nPerplexity: ',
         #     self.ldamodel.log_perplexity(self.corpus))  # a measure of how good the model is. lower the better.

        # Compute Coherence Score
        coherence_model_lda = CoherenceModel(model=self.ldamodel, texts=ldaTokens, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        print('\nCoherence Score: ', coherence_lda, '\r\n')

    '''def display(self):
        vis = pyLDAvis.gensim.prepare(self.ldamodel, self.corpus, self.dictionary)
        pyLDAvis.show(vis)'''

    def saveOnDB(self, lezione):

        topics = self.ldamodel.print_topics(num_words=4)
        numTopic = 0

        for topic in topics:
            ldaTopic = LdaTopic(lezione=lezione, numTopic=numTopic)
            ldaTopic.save()
            numTopic += 1
            for word in topic[1].split(" + "):
                data = word.split('*')
                ldaWord = LdaWord(ldaTopic=ldaTopic, word=data[1], weight=data[0])
                ldaWord.save()
