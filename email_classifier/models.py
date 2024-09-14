from django.db import models


# class SpamEmail(models.Model):
#     email_id = models.CharField(max_length=255)
#     subject = models.CharField(max_length=255)
#     sender = models.CharField(max_length=255)
#     body = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)


class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
