from django.contrib.auth.models import Group

from .Author import *
from .DepositNote import *
from .Deposit import *
from .LectureNote import *
from .PrintingQuota import *
from .Shift import *
from .User import *

admin.site.site_header = "SkriptenTool"
admin.site.site_title = "SkriptenTool"
admin.site.index_title = "Verwaltung"
admin.site.unregister(Group)


