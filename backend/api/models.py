from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField()
    summary = models.JSONField(default=dict)
    # NEW: store the raw CSV rows
    raw_data = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name
