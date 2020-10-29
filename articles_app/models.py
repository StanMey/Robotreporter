from django.db import models
from django.contrib.postgres.fields import JSONField


class Stocks(models.Model):
    indexx = models.CharField(max_length=100)
    component = models.CharField(max_length=100, default=None)
    # abs_delta = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # abs_perc = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    volume = models.IntegerField(default=None)
    s_open = models.DecimalField(max_digits=8, decimal_places=3)
    s_high = models.DecimalField(max_digits=8, decimal_places=3)
    s_low = models.DecimalField(max_digits=8, decimal_places=3)
    s_close = models.DecimalField(max_digits=8, decimal_places=3)
    date = models.DateTimeField()

    def __str__(self):
        return "{0} - {1} on {2}; close: {3}".format(self.component, self.indexx, self.date, self.s_close)

    def __repr__(self):
        return "{0} - {1} - {2}".format(self.component, self.date, self.s_close)


class Observations(models.Model):
    serie = models.CharField(max_length=100, default=None)
    period_begin = models.DateTimeField()
    period_end = models.DateTimeField()
    pattern = models.CharField(max_length=200, default=None)
    observation = models.TextField()
    relevance = models.DecimalField(max_digits=4, decimal_places=2)
    meta_data = JSONField(default=dict)

    def __str__(self):
        return "{0} with {1}; on: {2} / {3}".format(self.serie, self.pattern, self.period_begin.strftime("%Y-%m-%d"), self.period_end.strftime("%Y-%m-%d"))

    def __repr__(self):
        return "{0} - {1}/{2} - {3}".format(self.serie, self.period_begin.strftime("%Y-%m-%d"), self.period_end.strftime("%Y-%m-%d"), self.observation)


class Articles(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField()
    author = models.CharField(max_length=100)
    AI_version = models.FloatField(null=True)
    meta_data = JSONField(default=dict)

    def __str__(self):
        return "{0} - {1} - {2}".format(self.date, self.author, self.title)

    def __repr__(self):
        return "{0} - {1} - {2}".format(self.date, self.author, self.title)
