from django.conf import settings
from service import decode
from storage import read_json

def state():
    folder = settings.BASE_DIR / 'data'
    return decode(read_json(folder / ('runtime.json' if (folder / 'runtime.json').exists() else 'seed.json')))
