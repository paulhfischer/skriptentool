import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


# overwrite existing file instead of renaming it
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
