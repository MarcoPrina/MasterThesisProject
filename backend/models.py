from django.db import models


class Corsi(models.Model):
    kiro_url = models.URLField(max_length=200)
    nome = models.CharField(max_length=200)

    def __str__(self):
        return self.nome


class Lezioni(models.Model):
    video_url = models.URLField(max_length=200)
    kiro_url = models.URLField(max_length=200, unique=True)
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
