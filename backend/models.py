from django.db import models


class Corso(models.Model):
    kiro_url = models.URLField(max_length=200)
    nome = models.CharField(max_length=200, unique=True, db_index=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Corsi"


class Lezione(models.Model):
    video_url = models.URLField('URL della videolezione', max_length=200, null=True, blank=True,
                                help_text='Inserire url di Vimeo o Youtube')
    process_lda = models.BooleanField('Eseguire LDA', default=True)
    kiro_url = models.URLField('URL lezione su kiro', max_length=200)
    nome = models.CharField(max_length=200)
    corso = models.ForeignKey(Corso, on_delete=models.CASCADE)
    processata = models.BooleanField(default=False, auto_created=True)
    video = models.FileField('Carica videolezione', upload_to='Media/Video/', null=True, blank=True, )

    def __str__(self):
        return self.corso.nome + ': ' + self.nome

    class Meta:
        verbose_name_plural = "Lezioni"


class Word(models.Model):
    word = models.CharField('Parola', db_index=True, max_length=50)
    lezione = models.ForeignKey(Lezione, on_delete=models.CASCADE)
    time_stamp = models.TimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name_plural = "Words"


class WordCount(models.Model):
    word = models.CharField(max_length=50)
    lezione = models.ForeignKey(Lezione, on_delete=models.CASCADE)
    count = models.IntegerField('Conteggio', db_index=True)
    tf = models.FloatField()

    def __str__(self):
        return self.word + ' ' + str(self.count)

    class Meta:
        verbose_name_plural = "WordsCounts"


class Binomio(models.Model):
    word1 = models.CharField('Prima parola', max_length=50)
    word2 = models.CharField('Seconda parola', max_length=50)
    lezione = models.ForeignKey(Lezione, on_delete=models.CASCADE)
    time_stamp = models.TimeField(auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name_plural = "Binomi"
        indexes = [
            models.Index(fields=['word1', 'word2']),
        ]

    def __str__(self):
        return self.word1 + ' ' + self.word2


class BinomioCount(models.Model):
    binomio = models.CharField(max_length=50)
    lezione = models.ForeignKey(Lezione, on_delete=models.CASCADE)
    count = models.IntegerField('Conteggio', db_index=True)
    tf = models.FloatField()

    def __str__(self):
        return self.binomio + ' ' + str(self.count)

    class Meta:
        verbose_name_plural = "BinomiCounts"


class LdaTopic(models.Model):
    lezione = models.ForeignKey(Lezione, on_delete=models.CASCADE)
    numTopic = models.IntegerField()

    def __str__(self):
        return self.lezione.nome + ', topic #' + str(self.numTopic)

    class Meta:
        verbose_name_plural = "LdaTopics"


class LdaWord(models.Model):
    ldaTopic = models.ForeignKey(LdaTopic, on_delete=models.CASCADE)
    word = models.CharField(max_length=50)
    weight = models.FloatField()

    def __str__(self):
        return self.ldaTopic.__str__() + ': ' + self.word + ' * ' + str(self.weight)

    class Meta:
        verbose_name_plural = "LdaWords"
