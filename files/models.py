from django.db import models
from django.conf import settings
import uuid


class SecureFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='files'
    )

    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=255)

    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name