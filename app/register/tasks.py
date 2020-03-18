import io
import logging

from celery import shared_task

from common.analytics import statsd
from common.pdf import fill_form

from .models import Registration

logger = logging.getLogger("register")


@shared_task
@statsd.timed("turnout.register.process_registration_submission")
def process_registration_submission(registration_pk, state_id_number, is_18_or_over):
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
    registration_data["state"] = registration.state.code
    if registration.previous_state:
        registration_data["previous_state"] = registration.previous_state.code
    if registration.mailing_state:
        registration_data["mailing_state"] = registration.mailing_state.code
    registration_data["date_of_birth"] = registration.date_of_birth.strftime("%m/%d/%Y")
    registration_data["is_18_or_over"] = is_18_or_over
    registration_data["state_id_number"] = state_id_number

    if registration.title:
        title_field = registration.title.value.lower()
        registration_data[f"title_{title_field}"] = True
    if registration.previous_title:
        title_field = registration.previous_title.value.lower()
        registration_data[f"previous_title_{title_field}"] = True

    if registration.suffix:
        suffix_field = registration.suffix.replace(".", "").lower()
        registration_data[f"suffix_{suffix_field}"] = True
    if registration.previous_suffix:
        suffix_field = registration.previous_suffix.replace(".", "").lower()
        registration_data[f"previous_suffix_{suffix_field}"] = True

    # fill from dict
    fill_form(template_pdf, filled_pdf, registration_data)

    # TODO upload to s3
    # TEMP copy to /app/ to be visible
    with open("/app/tmp/register-out.pdf", "wb") as tmp_out:
        tmp_out.write(filled_pdf.getbuffer())

    # remove temporary file
    filled_pdf.close()
