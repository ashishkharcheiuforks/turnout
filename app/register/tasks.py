import logging
import shutil
import io

from celery import shared_task

from common.analytics import statsd
from common.pdf import fill_form

from .models import Registration

logger = logging.getLogger("register")


@shared_task
@statsd.timed("turnout.register.process_registration_submission")
def process_registration_submission(registration_pk, state_id):
    registration = Registration.objects.get(pk=registration_pk)

    # TODO, select template based on state
    template_path = "register/templates/pdf/eac-nvra.pdf"

    # open file objects
    template_pdf = open(template_path, "rb")
    filled_pdf = io.BytesIO()

    # convert Registration to dict
    registration_data = registration.__dict__
    # some fields need to be converted to string representation
    # state, date_of_birth, enums

    # fill from dict
    fill_form(template_pdf, filled_pdf, registration_data)

    # TODO upload to s3
    # TEMP copy to /app/ to be visible
    with open("/app/tmp/register-out.pdf", "wb") as tmp_out:
        tmp_out.write(filled_pdf.getbuffer())

    # remove temporary file
    filled_pdf.close()
