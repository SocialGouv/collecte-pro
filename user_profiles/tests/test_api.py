from pytest import mark

from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from rest_framework.test import APIClient

from tests import factories, utils
from user_profiles.models import Access, UserProfile

pytestmark = mark.django_db
client = APIClient()

User = get_user_model()


def search_user_by_username(current_user, username):
    utils.login(client, user=current_user)
    url = f"{reverse('api:user-list')}?search={username}"
    return client.get(url)


def test_logged_in_user_can_list_users():
    user_profile = factories.UserProfileFactory()
    user = user_profile.user
    utils.login(client, user=user)
    url = reverse('api:user-list')
    response = client.get(url)
    assert response.status_code == 200


def test_logged_in_user_can_search_user_by_username():
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    login_user = inspector.user
    target_user = factories.UserProfileFactory()
    control = factories.ControlFactory()
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    target_access = factories.AccessFactory(
        userprofile=target_user,
        control=control,
    )

    response = search_user_by_username(login_user, target_user.user.username)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['email'] == target_user.user.username


def test_cannot_search_audited_user_by_username_if_associated_with_deleted_control():
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    login_user = audited.user
    target_user = factories.UserProfileFactory()
    control = factories.ControlFactory()
    audited_access = factories.AccessFactory(
        userprofile=audited,
        control=control,
        access_type=Access.REPONDANT,
    )
    target_access = factories.AccessFactory(
        userprofile=target_user,
        control=control,
    )

    control.delete()
    control.save()

    response = search_user_by_username(login_user, target_user.user.username)

    # Sucessful query with no results
    assert response.status_code == 200
    assert len(response.data) == 0


def test_can_search_inspector_user_by_username_if_associated_with_deleted_control():
    control = factories.ControlFactory()
    inspector = utils.make_inspector_user(control)
    target_user = utils.make_audited_user(control)
    control.delete()
    control.save()

    response = search_user_by_username(inspector, target_user.username)

    # Sucessful query with no results
    assert response.status_code == 200
    assert len(response.data) == 1


def test_inspector_can_create_user():
    parameter = factories.ParameterFactory()
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    post_data = {
        'first_name': 'Marcel',
        'last_name': 'Proust',
        'profile_type': UserProfile.AUDITED,
        'email': 'marcel@proust.com',
        'control': control.id
    }
    utils.login(client, user=inspector.user)
    url = reverse('api:user-list')
    count_before = User.objects.count()
    response = client.post(url, post_data)
    count_after = User.objects.count()
    assert count_after == count_before + 1
    assert response.status_code == 201


def test_inspector_can_update_an_existing_user():
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    existing_user = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    existing_user_access = factories.AccessFactory(
        userprofile=existing_user,
        control=control,
    )
    post_data = {
        'first_name': 'Marcel',
        'last_name': 'Proust',
        'profile_type': UserProfile.AUDITED,
        'organization': '',
        'email': existing_user.user.email,
    }
    assert existing_user.user.first_name != 'Marcel'
    assert existing_user.user.last_name != 'Proust'

    utils.login(client, user=inspector.user)
    url = reverse('api:user-list')
    count_before = User.objects.count()
    client.post(url, post_data)

    count_after = User.objects.count()
    modified_user = UserProfile.objects.get(pk=existing_user.pk)
    assert count_after == count_before
    assert modified_user.user.first_name == 'Marcel'
    assert modified_user.user.last_name == 'Proust'


def test_inspector_can_update_an_existing_user_with_different_casing():
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    existing_user = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    existing_user_access = factories.AccessFactory(
        userprofile=existing_user,
        control=control,
        access_type=Access.REPONDANT,
    )

    post_data = {
        'first_name': 'Marcel',
        'last_name': 'Proust',
        'profile_type': UserProfile.AUDITED,
        'organization': '',
        'email': existing_user.user.email.upper(),  # uppercase the email
    }
    assert existing_user.user.first_name != 'Marcel'
    assert existing_user.user.last_name != 'Proust'

    utils.login(client, user=inspector.user)
    url = reverse('api:user-list')
    count_before = User.objects.count()
    client.post(url, post_data)

    count_after = User.objects.count()
    modified_user = UserProfile.objects.get(pk=existing_user.pk)
    # Update has happened successfully
    assert count_after == count_before
    assert modified_user.user.first_name == 'Marcel'
    assert modified_user.user.last_name == 'Proust'
    # Email is still lowercase
    assert modified_user.user.email.lower() == modified_user.user.email


def test_can_associate_a_control_to_an_existing_user():
    parameter = factories.ParameterFactory()
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    existing_user = factories.UserFactory()
    post_data = {
        'first_name': existing_user.first_name,
        'last_name': existing_user.last_name,
        'profile_type': 'audited',
        'email': existing_user.email,
        'organization': '',
        'control': control.id
    }
    utils.login(client, user=inspector.user)
    assert control not in [access.control for access in existing_user.profile.access.all()]
    url = reverse('api:user-list')
    count_before = User.objects.count()
    response = client.post(url, post_data)
    count_after = User.objects.count()
    assert response.status_code == 201
    assert count_after == count_before
    assert control in [access.control for access in existing_user.profile.access.all()]


def test_audited_cannot_create_user():
    factories.ParameterFactory()
    audited = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    control = factories.ControlFactory()
    audited_access = factories.AccessFactory(
        userprofile=audited,
        control=control,
        access_type=Access.REPONDANT,
    )
    post_data = {
        'first_name': 'Inspector',
        'last_name': 'Gadget',
        'profile_type': UserProfile.INSPECTOR,
        'email': 'inspector@gadget.com',
        'control': control.id
    }
    utils.login(client, user=audited.user)
    url = reverse('api:user-list')
    count_before = User.objects.count()
    response = client.post(url, post_data)
    count_after = User.objects.count()
    assert count_after == count_before
    assert response.status_code >= 300


def test_cannot_create_user_when_control_is_deleted():
    factories.ParameterFactory()
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    post_data = {
        'first_name': 'Marcel',
        'last_name': 'Proust',
        'profile_type': UserProfile.AUDITED,
        'email': 'marcel@proust.com',
        'control': control.id
    }
    utils.login(client, user=inspector.user)
    url = reverse('api:user-list')
    count_before = User.objects.count()
    control.delete()
    response = client.post(url, post_data)
    count_after = User.objects.count()
    assert count_after == count_before
    assert 400 <= response.status_code < 500


def test_inspector_cannot_alter_a_control_that_is_not_accessible_to_him():
    factories.ParameterFactory()
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    existing_user = factories.UserFactory()
    assert control not in [access.control for access in inspector.access.all()]
    assert control not in [access.control for access in existing_user.profile.access.all()]
    post_data = {
        'first_name': existing_user.first_name,
        'last_name': existing_user.last_name,
        'profile_type': UserProfile.AUDITED,
        'email': existing_user.email,
        'organization': '',
        'control': control.id
    }
    utils.login(client, user=inspector.user)
    url = reverse('api:user-list')
    count_before = User.objects.count()
    response = client.post(url, post_data)
    count_after = User.objects.count()
    assert response.status_code >= 300
    assert count_after == count_before
    assert control not in [access.control for access in existing_user.profile.access.all()]


def test_inspector_can_remove_user_from_control():
    parameter = factories.ParameterFactory()
    someone = factories.UserProfileFactory(profile_type=UserProfile.AUDITED)
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    someone_access = factories.AccessFactory(
        userprofile=someone,
        control=control,
        access_type=Access.REPONDANT,
    )
    utils.login(client, user=inspector.user)
    url = reverse('api:user-remove-control', args=[someone.pk])
    count_before = User.objects.filter(profile__access__control=control).count()
    response = client.post(url, {'control': control.pk})
    count_after = User.objects.filter(profile__access__control=control).count()
    assert count_after == count_before - 1
    assert response.status_code == 200


def test_logged_in_user_can_get_current_user():
    user_profile = factories.UserProfileFactory()
    user = user_profile.user
    utils.login(client, user=user)
    url = reverse('api:user-current')
    response = client.get(url)
    assert response.status_code == 200


def test_new_audited_user_should_have_the_file_reporting_flag_activated():
    parameter = factories.ParameterFactory()
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    post_data = {
        'first_name': 'Marcel',
        'last_name': 'Proust',
        'profile_type': UserProfile.AUDITED,
        'email': 'marcel@proust.com',
        'control': control.id
    }
    utils.login(client, user=inspector.user)
    url = reverse('api:user-list')
    count_before = User.objects.count()
    response = client.post(url, post_data)
    count_after = User.objects.count()
    assert count_after == count_before + 1
    assert response.status_code == 201
    new_user = User.objects.get(email='marcel@proust.com')
    assert new_user.profile.send_files_report


def test_new_inspector_user_should_have_the_file_reporting_flag_activated():
    parameter = factories.ParameterFactory()
    inspector = factories.UserProfileFactory(profile_type=UserProfile.INSPECTOR)
    control = factories.ControlFactory()
    inspector_access = factories.AccessFactory(
        userprofile=inspector,
        control=control,
        access_type=Access.DEMANDEUR,
    )
    post_data = {
        'first_name': 'Inspector',
        'last_name': 'Gadget',
        'profile_type': UserProfile.INSPECTOR,
        'email': 'inspector@gadget.com',
        'control': control.id
    }
    utils.login(client, user=inspector.user)
    url = reverse('api:user-list')
    count_before = User.objects.count()
    response = client.post(url, post_data)
    count_after = User.objects.count()
    assert count_after == count_before + 1
    assert response.status_code == 201
    new_user = User.objects.get(email='inspector@gadget.com')
    assert new_user.profile.send_files_report
