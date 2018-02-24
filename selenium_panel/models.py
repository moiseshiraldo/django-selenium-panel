from celery.result import AsyncResult
from django.db import models


class Browser(models.Model):
    """
    Stores a running Selenium browser
    """
    FIREFOX = "firefox"
    CHROME = "chrome"
    EDGE = "edge"
    SAFARI = "safari"
    DRIVER_CHOICES = (
        (FIREFOX, "Firefox"),
        (CHROME, "Chrome"),
        (EDGE, "Edge"),
        (SAFARI, "Safari"),
    )
    service_url = models.CharField(primary_key=True, max_length=100)
    session_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True)
    platform = models.CharField(max_length=50, blank=True)
    driver = models.CharField(max_length=20, choices=DRIVER_CHOICES)
    running_task = models.CharField(max_length=50, blank=True, null=True)

    @property
    def status(self):
        if self.running_task:
            result = AsyncResult(self.running_task)
            if result.failed():
                return "Failed"
            if not result.ready():
                return "Running"
        return "Idle"

    def as_dict(self):
        return {
            'service_url': self.service_url,
            'username': self.username,
            'platform': self.platform,
            'driver': self.driver,
            'status': self.status,
        }
