from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_pics', blank=True)
    last_login = models.DateTimeField(default=timezone.now)
    storage_limit = models.IntegerField(default=20000000000)  # 20GB default

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def storage_percentage(self):
        # Calculate total space used
        total_used_space = self.user.storedfile_set.aggregate(total_size=models.Sum('file_size'))['total_size'] or 0
        # Calculate percentage used
        if self.storage_limit > 0:
            percentage = (total_used_space / self.storage_limit) * 100
            return min(percentage, 100)  # Cap at 100%
        return 0


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Password(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_entries')
    website = models.CharField(max_length=200)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.website} - {self.username}"
    

# passwords/models.py
class StoredFile(models.Model):
    FILE_TYPES = (
        ('photo', 'Photo'),
        ('document', 'Document'),
        ('music', 'Music'),
        ('video', 'Video'),
        ('other', 'Other'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='user_files')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    shared_with = models.ManyToManyField(User, related_name='shared_files', blank=True)
    file_size = models.BigIntegerField(default=0) 

    def save(self, *args, **kwargs):
        # Automatically update file_size before saving
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file.name



class StoragePackage(models.Model):
    name = models.CharField(max_length=100)
    storage_limit = models.IntegerField()  # in bytes
    price = models.DecimalField(max_digits=6, decimal_places=2)
    icon_color = models.CharField(max_length=7, default='#000000')  # Hex color code

    def __str__(self):
        return self.name