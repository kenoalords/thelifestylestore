from django.db import models

class ActiveProducts(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class ActiveProductSliders(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
