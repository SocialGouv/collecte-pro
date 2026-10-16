import zipfile

from pytest import mark

from reporting.tasks import generate_disk_usage_report_file, get_disk_usage_report_path
from tests import factories


pytestmark = mark.django_db


def test_generate_disk_usage_report_file_writes_zip_with_two_csvs(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)
    response_file = factories.ResponseFileFactory()

    generate_disk_usage_report_file()

    report_path = get_disk_usage_report_path()
    assert report_path is not None
    assert report_path.endswith('.zip')

    with zipfile.ZipFile(report_path) as zip_file:
        names = zip_file.namelist()
        assert any(name.startswith('poids_fichiers_espaces_depot_') for name in names)
        assert any(name.startswith('poids_fichiers_questionnaires_') for name in names)

        control = response_file.question.theme.questionnaire.control
        espaces_csv_name = next(name for name in names if name.startswith('poids_fichiers_espaces_depot_'))
        espaces_csv_content = zip_file.read(espaces_csv_name).decode('utf-8')
        assert control.reference_code in espaces_csv_content


def test_generate_disk_usage_report_file_clears_previous_reports(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)
    factories.ResponseFileFactory()

    generate_disk_usage_report_file()
    first_report_path = get_disk_usage_report_path()

    generate_disk_usage_report_file()
    second_report_path = get_disk_usage_report_path()

    reports_dir = tmp_path / "rapports_poids_fichiers"
    all_reports = list(reports_dir.glob("collecte-pro_poids_fichiers_*.zip"))

    assert len(all_reports) == 1
    assert first_report_path == second_report_path
