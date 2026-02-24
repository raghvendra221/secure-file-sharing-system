from django.utils import timezone
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
    encrypted_file_key = models.BinaryField(null=True, blank=True)
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name


class FileShareToken(models.Model):
    file = models.ForeignKey(SecureFile, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    expiry_time = models.DateTimeField()
    max_downloads = models.IntegerField(default=1)
    current_downloads = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expiry_time

    def __str__(self):
        return f"Token for {self.file.original_name}"