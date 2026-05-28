from django.db import models


class TempMseUpload(models.Model):
    """A model just to store uploaded data files so we can retrieve them by id from a session."""
    file = models.FileField(upload_to="temp_mse_uploads/")
    created_at = models.DateTimeField(auto_now_add=True)
