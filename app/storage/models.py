import datetime

import smalluuid
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django_smalluuid.models import SmallUUIDField, uuid_default
from enumfields import EnumField

from common import enums
from common.analytics import statsd
from common.utils.models import TimestampModel, UUIDModel

from .backends import HighValueStorage


def storage_expire_date_time():
    return now() + datetime.timedelta(hours=settings.FILE_EXPIRATION_HOURS)


class StorageItem(UUIDModel, TimestampModel):
    token = SmallUUIDField(default=uuid_default())
    app = EnumField(enums.FileType)
    file = models.FileField(storage=HighValueStorage())
    email = models.EmailField(blank=True, null=True)
    expires = models.DateTimeField(default=storage_expire_date_time)

    class Meta:
        ordering = ["-created_at"]

    def refresh_token(self):
        self.token = smalluuid.SmallUUID()
        self.expires = storage_expire_date_time()
        self.save(update_fields=["token", "expires"])
        statsd.increment("turnout.storage.refresh_token")
        return self.token
