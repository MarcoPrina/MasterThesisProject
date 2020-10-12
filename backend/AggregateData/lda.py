import gensim
from gensim import corpora
from gensim.models import CoherenceModel

from backend.models import LdaCorso, LdaLezione


class LDA():

    def __init__(self):
        self.mallet_path = 'mallet-2.0.8/mallet-2.0.8/bin/mallet'

    def findTopicFromTokens(self, tokens, nTopic, posTag=['']):
        buffTokens = []
        ldaTokens = []
        for num, token in enumerate(tokens):
            if token['pos'].startswith(tuple(posTag)) and len(token['word']) > 2:
                buffTokens.append(token['word'][:-1])
            if len(buffTokens) > 1 and ('.' in token['word'] or '?' in token['word'] or '!' in token['word']):
                ldaTokens.append(buffTokens)
                buffTokens = []

        ldaTokens.append(buffTokens)
        self.findTopicFromSenteces(ldaTokens, nTopic)

    def findTopicFromSenteces(self, sentences, nTopic):
        dictionary = corpora.Dictionary(sentences)
        corpus = [dictionary.doc2bow(text) for text in sentences]

        # self.ldamodel = gensim.models.ldamodel.LdaModel(self.corpus, num_topics=nTopic, id2word=self.dictionary, passes=15)

        self.ldamodel = gensim.models.wrappers.LdaMallet(self.mallet_path, corpus=corpus, num_topics=nTopic,
                                                         id2word=dictionary)

        # self.ldamodel.save('model5.gensim')

        # Compute Perplexity
        # print('\nPerplexity: ',
        #     self.ldamodel.log_perplexity(self.corpus))  # a measure of how good the model is. lower the better.

        # Compute Coherence Score
        coherence_model_lda = CoherenceModel(model=self.ldamodel, texts=sentences, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        print('\nCoherence Score: ', coherence_lda, '\r\n')

    '''def display(self):
        vis = pyLDAvis.gensim.prepare(self.ldamodel, self.corpus, self.dictionary)
        pyLDAvis.show(vis)'''

    def saveOnDBLezione(self, lezione):
        LdaLezione.objects.filter(lezione=lezione).delete()
        topics = self.ldamodel.print_topics(num_words=4)
        lda = []

        for topic in topics:
            lda.append(topic[1].replace(" + ", ' '))

        ldaLezione = LdaLezione(lezione=lezione, lda=lda)
        ldaLezione.save()

    def saveOnDBCorso(self, corso):
        topics = self.ldamodel.print_topics(num_words=4)
        lda = []

        for topic in topics:
            lda.append(topic[1].replace(" + ", ' '))

        ldaCorso = LdaCorso(corso=corso, lda=lda)
        ldaCorso.save()
