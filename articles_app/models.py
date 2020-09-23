from django.db import models


class Stocks(models.Model):
    index = models.CharField(max_length=100)
    component = models.CharField(max_length=100, default=None)
    abs_delta = models.DecimalField(max_digits=8, decimal_places=2)
    abs_perc = models.DecimalField(max_digits=8, decimal_places=2)
    volume = models.IntegerField(default=None)
    s_open = models.DecimalField(max_digits=8, decimal_places=2)
    s_high = models.DecimalField(max_digits=8, decimal_places=2)
    s_low = models.DecimalField(max_digits=8, decimal_places=2)
    s_close = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField()

    def __str__(self):
        return "{0} - {1} on {2}; close: {3}".format(self.component, self.index, self.date, self.s_close)

    def __repr__(self):
        return "{0} - {1} - {2}".format(self.component, self.date, self.s_close)


class Articles(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField()
    author = models.CharField(max_length=100)
    AI_version = models.FloatField(null=True)

    def __str__(self):
        return "{0} - {1} - {2}".format(self.date, self.author, self.title)

    def __repr__(self):
        return "{0} - {1} - {2}".format(self.date, self.author, self.title)