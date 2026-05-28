from django.db import models

class TempMseUpload(models.Model):
    file = models.FileField(upload_to="temp_mse_uploads/")
    created_at = models.DateTimeField(auto_now_add=True)
