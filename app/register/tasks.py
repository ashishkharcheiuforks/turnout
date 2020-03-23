import io
import logging

from celery import shared_task

from common.analytics import statsd
from common.pdf import fill_form, join_files
from election.models import StateInformation

from .models import Registration

logger = logging.getLogger("register")


@shared_task
@statsd.timed("turnout.register.process_registration_submission")
def process_registration_submission(registration_pk, state_id_number, is_18_or_over):
    registration = Registration.objects.select_related().get(pk=registration_pk)

    # TODO, select template based on state
    template_path = "register/templates/pdf/eac-nvra.pdf"
    cover_path = "register/templates/pdf/cover.pdf"

    # open file objects
    template_pdf = open(template_path, "rb")
    cover_pdf = open(cover_path, "rb")
    joined_pdf = io.BytesIO()
    filled_pdf = io.BytesIO()

    # convert Registration to dict
    form_data = registration.__dict__
    # some fields need to be converted to string representation
    # state, date_of_birth, enums
    form_data["state"] = registration.state.code
    if registration.previous_state:
        form_data["previous_state"] = registration.previous_state.code
    if registration.mailing_state:
        form_data["mailing_state"] = registration.mailing_state.code
    form_data["date_of_birth"] = registration.date_of_birth.strftime("%m/%d/%Y")
    form_data["is_18_or_over"] = is_18_or_over
    form_data["state_id_number"] = state_id_number

    if registration.title:
        title_field = registration.title.value.lower()
        form_data[f"title_{title_field}"] = True
    if registration.previous_title:
        title_field = registration.previous_title.value.lower()
        form_data[f"previous_title_{title_field}"] = True

    if registration.suffix:
        suffix_field = registration.suffix.replace(".", "").lower()
        form_data[f"suffix_{suffix_field}"] = True
    if registration.previous_suffix:
        suffix_field = registration.previous_suffix.replace(".", "").lower()
        form_data[f"previous_suffix_{suffix_field}"] = True

    # get mailto address from StateInformation
    # later this will be more complicated...
    try:
        state_mailto_address = StateInformation.objects.only("field_type", "text").get(
            state=registration.state,
            field_type__slug="registration_nvrf_submission_address",
        ).text
    except StateInformation.DoesNotExist:
        state_mailto_address = ""
    # split by linebreaks, because each line is a separate field in the PDF
    for num, line in enumerate(state_mailto_address.splitlines()):
        form_data[f"mailto_line_{num+1}"] = line

    # get mailing deadline from StateInformation
    try:
        state_mail_deadline = StateInformation.objects.only("field_type", "text").get(
            state=registration.state, field_type__slug="registration_deadline_mail",
        ).text.lower()
        if state_mail_deadline.split()[0] in ["postmarked", "received"]:
            state_deadline = f"Your form must be {state_mail_deadline}."
        else:
            state_deadline = f"Your form must arrive by {state_mail_deadline}."
    except StateInformation.DoesNotExist:
        state_deadline = "Mail your form as soon as possible."
    form_data["state_deadlines"] = state_deadline

    # join cover pages
    join_files([cover_pdf, template_pdf], joined_pdf)

    with open("/app/tmp/register-joined.pdf", "wb") as tmp_out:
        tmp_out.write(joined_pdf.getbuffer())

    # reset buffer on joined_pdf
    joined_pdf.seek(0)

    # fill from dict
    fill_form(joined_pdf, filled_pdf, form_data)

    # TODO upload to s3
    # TEMP copy to /app/ to be visible
    with open("/app/tmp/register-out.pdf", "wb") as tmp_out:
        tmp_out.write(filled_pdf.getbuffer())

    # remove temporary file
    filled_pdf.close()
