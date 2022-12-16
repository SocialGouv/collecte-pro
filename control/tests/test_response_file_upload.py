from pytest import mark

from django.shortcuts import reverse
from django.test import override_settings

from control.models import ResponseFile
from tests import factories, utils
from user_profiles.models import Access, UserProfile


pytestmark = mark.django_db


def test_audited_can_upload_question_file(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_file.open(),
        'question_id': [question.id]
    }
    response = client.post(url, post_data, format='multipart')
    assert response.status_code == 200
    count_after = ResponseFile.objects.count()
    assert count_after == count_before + 1


def test_cannot_upload_question_file_if_control_is_deleted(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_file.open(),
        'question_id': [question.id]
    }
    question.theme.questionnaire.control.delete()
    response = client.post(url, post_data, format='multipart')
    assert 400 <= response.status_code < 500
    count_after = ResponseFile.objects.count()
    assert count_after == count_before


def test_audited_cannot_upload_question_file_if_questionnaire_is_draft(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = True
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_file.open(),
        'question_id': [question.id]
    }
    response = client.post(url, post_data, format='multipart')
    assert response.status_code == 404
    count_after = ResponseFile.objects.count()
    assert count_after == count_before


def test_cannot_upload_question_file_in_a_control_user_is_not_in(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    assert question.theme.questionnaire.control not in [access.control for access in audited.access.all() if access.control.active()]
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_file.open(),
        'question_id': [question.id]
    }
    response = client.post(url, post_data, format='multipart')
    assert 400 <= response.status_code < 500
    count_after = ResponseFile.objects.count()
    assert count_after == count_before


def test_inspector_cannot_upload_question_file(client):
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    question = factories.QuestionFactory()
    inspector.access.create(
        userprofile=inspector,
        control=question.theme.questionnaire.control,
        access_type=Access.DEMANDEUR,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=inspector.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_file.open(),
        'question_id': [question.id]
    }
    response = client.post(url, post_data, format='multipart')
    assert 400 <= response.status_code < 500
    count_after = ResponseFile.objects.count()
    assert count_after == count_before


def test_audited_cannot_upload_exe_file(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_exe_file.open(),
        'question_id': [question.id]
    }
    response = client.post(url, post_data, format='multipart')
    assert response.status_code == 403
    count_after = ResponseFile.objects.count()
    assert count_after == count_before


def test_missing_question_id_raise_bad_request(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_file.open(),
        'no_question_id': [question.id]
    }
    response = client.post(url, post_data, format='multipart')
    assert response.status_code == 400
    count_after = ResponseFile.objects.count()
    assert count_after == count_before


@override_settings(UPLOAD_FILE_MAX_SIZE_MB=0.01)
def test_audited_cannot_upload_file_if_size_exceed(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_file.open(),
        'question_id': [question.id]
    }
    response = client.post(url, post_data, format='multipart')
    assert response.status_code == 403
    count_after = ResponseFile.objects.count()
    assert count_after == count_before


@override_settings(UPLOAD_FILE_EXTENSION_BLACKLIST=('.sh',))
def test_audited_cannot_upload_file_if_blaklist_extension(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse('response-upload')
    count_before = ResponseFile.objects.count()
    post_data = {
        'file': factories.dummy_text_file_with_sh_extension.open(),
        'question_id': [question.id]
    }
    response = client.post(url, post_data, format='multipart')
    assert response.status_code == 403
    count_after = ResponseFile.objects.count()
    assert count_after == count_before


def test_uploaded_pdf_response_file_is_same_size(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse("response-upload")
    dummy_file = factories.dummy_file
    post_data = {
        "file": dummy_file.open(),
        "question_id": [question.id]
    }
    response = client.post(url, post_data, format="multipart")
    response_file = ResponseFile.objects.last()
    assert response_file.file.size == dummy_file.size


def test_uploaded_xls_response_file_is_same_size(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse("response-upload")
    dummy_file = factories.dummy_xlsx_file
    post_data = {
        "file": dummy_file.open(),
        "question_id": [question.id]
    }
    response = client.post(url, post_data, format="multipart")
    response_file = ResponseFile.objects.last()
    assert response_file.file.size == dummy_file.size


def test_uploaded_doc_response_file_is_same_size(client):
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    question = factories.QuestionFactory()
    audited.access.create(
        userprofile=audited,
        control=question.theme.questionnaire.control,
        access_type=Access.REPONDANT,
    )
    question.theme.questionnaire.is_draft = False
    question.theme.questionnaire.save()
    utils.login(client, user=audited.user)
    url = reverse("response-upload")
    dummy_file = factories.dummy_docx_file
    post_data = {
        "file": dummy_file.open(),
        "question_id": [question.id]
    }
    response = client.post(url, post_data, format="multipart")
    response_file = ResponseFile.objects.last()
    print(response_file)
    assert response_file.file.size == dummy_file.size
