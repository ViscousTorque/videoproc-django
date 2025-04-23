"""Video processing model"""
from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    processed = models.BooleanField(default=False)
    output_file = models.FileField(upload_to='processed/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    # using choices here allows the code to save as done and Admin view Done - see choices
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'),
                                                      ('processing', 'Processing'),
                                                      ('failed', 'Failed'),
                                                      ('done', 'Done')],
                                                      default='pending')
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
