import factory

from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify

from pytest_factoryboy import register
from faker import Factory as FakerFactory

faker = FakerFactory.create('fr_FR')


with open(settings.BASE_DIR + '/tests/data/test.pdf', 'rb') as file_handler:
    dummy_file = SimpleUploadedFile(
        name='test.pdf',
        content=file_handler.read(),
        content_type='application/pdf',
    )

with open(settings.BASE_DIR + '/tests/data/test.exe', 'rb') as file_handler:
    dummy_exe_file = SimpleUploadedFile(
        name='test.exe',
        content=file_handler.read(),
        content_type='application/x-dosexec',
    )

with open(settings.BASE_DIR + '/tests/data/test.sh', 'rb') as file_handler:
    dummy_text_file_with_sh_extension = SimpleUploadedFile(
        name='test.sh',
        content=file_handler.read(),
        content_type='text/plain',
    )

with open(settings.BASE_DIR + '/tests/data/test.xlsx', 'rb') as file_handler:
    dummy_xlsx_file = SimpleUploadedFile(
        name='test.xlsx',
        content=file_handler.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

with open(settings.BASE_DIR + '/tests/data/test.docx', 'rb') as file_handler:
    dummy_docx_file = SimpleUploadedFile(
        name='test.docx',
        content=file_handler.read(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )


@register
class UserFactory(factory.django.DjangoModelFactory):
    first_name = factory.LazyFunction(faker.first_name)
    last_name = factory.LazyFunction(faker.last_name)
    email = factory.LazyFunction(faker.email)
    username = factory.LazyAttribute(lambda a: a.email)
    password = factory.PostGenerationMethodCall('set_password', '123')
    is_active = True
    is_staff = False

    class Meta:
        model = get_user_model()


@register
class UserProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    agreed_to_tos = True

    class Meta:
        model = 'user_profiles.UserProfile'


@register
class ControlFactory(factory.django.DjangoModelFactory):
    title = factory.LazyFunction(faker.name)
    reference_code = factory.LazyAttribute(
        lambda c: f"{datetime.today().year}_{slugify(c.title)[:25]}"
    )

    class Meta:
        model = 'control.Control'


@register
class AccessFactory(factory.django.DjangoModelFactory):
    userprofile = factory.SubFactory(UserProfileFactory)
    control = factory.SubFactory(ControlFactory)

    class Meta:
        model = 'user_profiles.Access'


@register
class QuestionnaireFactory(factory.django.DjangoModelFactory):
    title = factory.LazyFunction(faker.name)
    control = factory.SubFactory(ControlFactory)
    uploaded_file = dummy_file
    is_draft = True
    is_replied = False
    is_finalized = False

    class Meta:
        model = 'control.Questionnaire'


@register
class ThemeFactory(factory.django.DjangoModelFactory):
    title = factory.LazyFunction(faker.name)
    questionnaire = factory.SubFactory(QuestionnaireFactory)

    class Meta:
        model = 'control.Theme'


@register
class QuestionFactory(factory.django.DjangoModelFactory):
    description = factory.LazyFunction(faker.name)
    theme = factory.SubFactory(ThemeFactory)

    class Meta:
        model = 'control.Question'


@register
class ResponseFileFactory(factory.django.DjangoModelFactory):
    question = factory.SubFactory(QuestionFactory)
    author = factory.SubFactory(UserFactory)
    file = dummy_file

    class Meta:
        model = 'control.ResponseFile'


@register
class QuestionFileFactory(factory.django.DjangoModelFactory):
    question = factory.SubFactory(QuestionFactory)
    file = dummy_file

    class Meta:
        model = 'control.QuestionFile'


@register
class ParameterFactory(factory.django.DjangoModelFactory):
    code = "SUPPORT_EMAIL"
    title = "nowhere@example.org"
    name = "nowhere@example.org"
    url = "nowhere@example.org"

    class Meta:
        model = 'parametres.Parametre'
