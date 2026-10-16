import io
import zipfile
from unittest.mock import patch

from pytest import mark
from django.urls import reverse

from tests import factories


pytestmark = mark.django_db


def test_disk_usage_report_endpoints_flow(client, tmp_path, settings):
    """
    End-to-end check of the launch / poll / download flow wired in
    stats/views.py and stats/urls.py. The Celery `.delay()` call is patched
    to run the task synchronously (no broker available in tests), which is
    enough to validate the view <-> task <-> file <-> download wiring.
    """
    settings.MEDIA_ROOT = str(tmp_path)
    user = factories.UserFactory(is_staff=True)
    client.force_login(user)
    factories.ResponseFileFactory()

    # before launch: not ready
    response = client.get(reverse('stats:check_disk_usage_report'))
    assert response.status_code == 200
    assert response.json()['ready'] is False

    # launch (patch .delay to run synchronously, no broker in tests)
    from reporting.tasks import generate_disk_usage_report_file
    patch_target = 'stats.views.generate_disk_usage_report_file.delay'
    with patch(patch_target, side_effect=generate_disk_usage_report_file) as mocked_delay:
        response = client.post(reverse('stats:launch_disk_usage_report'))
        assert response.status_code == 200
        assert mocked_delay.called

    # now ready
    response = client.get(reverse('stats:check_disk_usage_report'))
    assert response.status_code == 200
    data = response.json()
    assert data['ready'] is True
    filename = data['filename']
    assert filename.startswith('collecte-pro_poids_fichiers_')

    # download
    response = client.get(reverse('stats:download_disk_usage_report'))
    assert response.status_code == 200
    assert response['Content-Disposition'] == f'attachment; filename="{filename}"'
    content = b"".join(response.streaming_content)
    with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
        assert len(zip_file.namelist()) == 2
