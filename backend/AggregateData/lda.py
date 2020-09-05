import os

from gensim import corpora
import gensim
import pyLDAvis.gensim
from gensim.models import CoherenceModel


class LDA():

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

        self.dictionary = corpora.Dictionary(ldaTokens)
        self.corpus = [self.dictionary.doc2bow(text) for text in ldaTokens]

        # self.ldamodel = gensim.models.ldamodel.LdaModel(self.corpus, num_topics=nTopic, id2word=self.dictionary, passes=15)

        mallet_path = 'mallet-2.0.8/mallet-2.0.8/bin/mallet'
        self.ldamodel = gensim.models.wrappers.LdaMallet(mallet_path, corpus=self.corpus , num_topics=nTopic, id2word=self.dictionary)

        # self.ldamodel.save('model5.gensim')

        # Compute Perplexity
        #print('\nPerplexity: ',
         #     self.ldamodel.log_perplexity(self.corpus))  # a measure of how good the model is. lower the better.

        # Compute Coherence Score
        coherence_model_lda = CoherenceModel(model=self.ldamodel, texts=ldaTokens, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        print('\nCoherence Score: ', coherence_lda, '\r\n')

    def display(self):
        '''lda_display = pyLDAvis.gensim.prepare(self.ldamodel, self.corpus, self.dictionary, sort_topics=False)
        pyLDAvis.display(lda_display)'''

        vis = pyLDAvis.gensim.prepare(self.ldamodel, self.corpus, self.dictionary)
        pyLDAvis.show(vis)

    def generateFile(self, directoryName: str, fileName='lda'):
        if os.path.exists('Outputs/' + directoryName + "/" + fileName + ".csv"):
            os.remove('Outputs/' + directoryName + "/" + fileName + ".csv")
        ldaFile = open('Outputs/' + directoryName + "/" + fileName + ".csv", "a")

        topics = self.ldamodel.print_topics(num_words=4)
        for topic in topics:
            ldaFile.write(topic[1].replace(" + ", ";") + '\r\n')
        ldaFile.close()
