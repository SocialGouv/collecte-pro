import io

from django.conf import settings
from django.core.files.base import ContentFile

from docxtpl import DocxTemplate, RichText

from .upload_path import questionnaire_file_path


class DocxMixin(object):
    """
    Helper class that provides docx utilities.
    """

    def to_rich_text(self, value):
        return RichText(value)


def generate_questionnaire_file(questionnaire):
    """
    Generate a word Docx document for the given questionnaire.
    The generated docment is based on a Docx template.
    This is made possible thanks to docxtepl Python package.
    """
    doc = DocxTemplate(settings.TEMPLATE_DIR + "/ecc/questionnaire.docx")
    context = {
        'questionnaire': questionnaire,
        'description': RichText(questionnaire.description)
    }
    # Note : autoescape is for HTML-escaping the user-provided questionnaire data, for XSS
    # protection.
    doc.render(context, autoescape=True)
    filename = f'Questionnaire-{questionnaire.numbering}.docx'
    relative_path = questionnaire_file_path(questionnaire, filename)
    # Save the generated docx in memory, then hand it off to the configured file storage
    # backend (local filesystem or S3, depending on settings) instead of writing directly
    # to disk, so the file ends up wherever DEFAULT_FILE_STORAGE / STORAGES["default"] points to.
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    questionnaire.generated_file.save(relative_path, ContentFile(buffer.read()), save=False)
    questionnaire.save()
