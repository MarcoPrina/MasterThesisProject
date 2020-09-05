from django.db import models


class Corsi(models.Model):
    kiro_url = models.CharField(max_length=200)
    nome = models.CharField(max_length=200)
    processata = models.BooleanField(default=False, auto_created=True)

    def __str__(self):
        return self.nome


class Lezioni(models.Model):
    video_url = models.CharField(max_length=200, unique=True)
    nome = models.CharField(max_length=200)
    processata = models.BooleanField(default=False, auto_created=True)
    corso = models.ForeignKey(Corsi, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Word(models.Model):
    word = models.CharField(max_length=50)
    lezione = models.ForeignKey(Lezioni, on_delete=models.CASCADE)
    time_stamp = models.CharField(max_length=15)

    def __str__(self):
        return self.word


class Binomi(models.Model):
    word1 = models.CharField(max_length=50)
    word2 = models.CharField(max_length=50)
    lezione = models.ForeignKey(Lezioni, on_delete=models.CASCADE)
    time_stamp = models.CharField(max_length=15)

    def __str__(self):
        return self.word1 + ' ' + self.word2
