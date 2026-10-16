import os

from dotenv import load_dotenv
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecc.settings")

app = Celery("ecc")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path, override=True)

app.config_from_object("django.conf:settings", namespace="CELERY")

# On set le nom de la queue utilisée par celery
# pour éviter de dependre de la file par defaut
# avec le risque que celle utilisée par le service
# soit différente de celle utilisée par l'app.
from django.conf import settings  # noqa: E402

app.conf.task_default_queue = settings.CELERY_QUEUE

app.autodiscover_tasks()
