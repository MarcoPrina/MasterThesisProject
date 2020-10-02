from django.db import models


class Corsi(models.Model):
    kiro_url = models.URLField(max_length=200)
    nome = models.CharField(max_length=200, unique=True, db_index=True)

    def __str__(self):
        return self.nome


class Lezioni(models.Model):
    video_url = models.URLField(max_length=200)
    kiro_url = models.URLField(max_length=200)
    nome = models.CharField(max_length=200)
    corso = models.ForeignKey(Corsi, on_delete=models.CASCADE)
    processata = models.BooleanField(default=False, auto_created=True)

    def __str__(self):
        return self.corso.nome + ': ' + self.nome


class Words(models.Model):
    word = models.CharField(db_index=True, max_length=50)
    lezione = models.ForeignKey(Lezioni, on_delete=models.CASCADE)
    time_stamp = models.TimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.word


class WordsCount(models.Model):
    word = models.CharField(max_length=50)
    lezione = models.ForeignKey(Lezioni, on_delete=models.CASCADE)
    count = models.IntegerField(db_index=True)
    tf = models.FloatField()

    def __str__(self):
        return self.word + ' ' + str(self.count)


class Binomi(models.Model):
    word1 = models.CharField(max_length=50)
    word2 = models.CharField(max_length=50)
    lezione = models.ForeignKey(Lezioni, on_delete=models.CASCADE)
    time_stamp = models.TimeField(auto_now=False, auto_now_add=False)

    class Meta:
        indexes = [
            models.Index(fields=['word1', 'word2']),
        ]

    def __str__(self):
        return self.word1 + ' ' + self.word2


class BinomiCount(models.Model):
    binomio = models.CharField(max_length=50)
    lezione = models.ForeignKey(Lezioni, on_delete=models.CASCADE)
    count = models.IntegerField(db_index=True)
    tf = models.FloatField()

    def __str__(self):
        return self.binomio + ' ' + str(self.count)


class LdaTopic(models.Model):
    lezione = models.ForeignKey(Lezioni, on_delete=models.CASCADE)
    numTopic = models.IntegerField()

    def __str__(self):
        return self.lezione.nome + ', topic #' + str(self.numTopic)


class LdaWord(models.Model):
    ldaTopic = models.ForeignKey(LdaTopic, on_delete=models.CASCADE)
    word = models.CharField(max_length=50)
    weight = models.FloatField()

    def __str__(self):
        return self.ldaTopic.__str__() + ': ' + self.word + ' * ' + str(self.weight)
