# Swiped from EveryVoter, which was swiped from Connect

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.timezone import now
from pytz import timezone
from smalluuid.smalluuid import SmallUUID

AttachmentStorageEngine = get_storage_class(
    import_path=settings.ATTACHMENT_STORAGE_ENGINE
)


def uniqify_filename(existing_filename):
    unique_code = str(SmallUUID())[:5]
    return f"{unique_code}.{existing_filename}"


private_bucket_name = getattr(settings, "AWS_STORAGE_PRIVATE_BUCKET_NAME", "")
querystring_expire = getattr(settings, "AWS_STORAGE_PRIVATE_URL_EXPIRATION", 60)


class AttachmentStorage(AttachmentStorageEngine):
    def get_available_name(self, name, max_length=None):
        # If the storage engine is S3, call _clean_name() to clean the name
        try:
            clean_name = self._clean_name(name)
        except AttributeError:
            clean_name = name

        # rsplit the filename on '/' so we have a 2 value list of the path and
        # filename
        splitname = clean_name.rsplit("/", 1)

        date = now().astimezone(timezone(settings.FILE_TIMEZONE)).strftime("%y%m%d")

        if len(splitname) == 2:
            final_name = f"{splitname[0]}/{date}.{uniqify_filename(splitname[1])}"
        else:
            final_name = f"{date}.{uniqify_filename(splitname[0])}"

        return final_name


class HighValueStorage(AttachmentStorage):
    default_acl = "private"
    secure_urls = True
    bucket_name = private_bucket_name

    # We have to override any `custom_domain` set in the settings file because our
    # storage engine will take that setting as a signal that all files have a
    # 'public' ACL
    custom_domain = None

    querystring_expire = querystring_expire
    querystring_auth = True
