import factory

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify

from pytest_factoryboy import register
from faker import Factory as FakerFactory

faker = FakerFactory.create('fr_FR')


dummy_file = SimpleUploadedFile(
    name='test.pdf',
    content=open(settings.BASE_DIR + '/tests/data/test.pdf', 'rb').read(),
    content_type='application/pdf')


dummy_exe_file = SimpleUploadedFile(
    name='test.exe',
    content=open(settings.BASE_DIR + '/tests/data/test.exe', 'rb').read(),
    content_type='application/x-dosexec')

dummy_text_file_with_sh_extension = SimpleUploadedFile(
    name='test.sh',
    content=open(settings.BASE_DIR + '/tests/data/test.sh', 'rb').read(),
    content_type='text/plain')


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
    reference_code = factory.LazyAttribute(lambda c: slugify(c.title))

    class Meta:
        model = 'control.Control'


@register
class QuestionnaireFactory(factory.django.DjangoModelFactory):
    title = factory.LazyFunction(faker.name)
    control = factory.SubFactory(ControlFactory)
    uploaded_file = dummy_file
    is_draft = True

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
