import os
from pathlib import Path
import yaml

os.chdir(Path(__file__).parent.parent)
ABS_PATH = Path(os.getcwd())

with open(os.path.join(ABS_PATH, 'config.yml'),  # type:ignore
            'r', encoding='utf-8') as f:
    config = yaml.safe_load(f.read()).get('bot', {})

TOKEN = config.get('token')
DEFAULT_PREFIX = config.get('prefix')
MAIN_SERVER = config.get('main_server')
DASHBOARD_CHANNEL = config.get('dashboard_channel')
SUPPORT_CHANNEL = config.get('support_channel')
STATISTICS_CHANNEL = config.get('statistics_channel')
SETTINGS_CHANNEL = config.get('settings_channel')
NEW_SERVERS_CHANNEL = config.get('new_servers_channel')
REDIRECT_URI = config.get('redirect_uri')
CLIENT_ID = config.get('client_id')
CLIENT_SECRET = config.get('client_secret')
FRONTLINES_URI_CONNECTION_STRING = config.get('frontlines_uri_connection_string')
CHAT_GPT_APIKEY = config.get('chat_gpt_apikey')

TRANSCRIPTS_USERNAME = config.get('transcripts_username')
TRANSCRIPTS_PASSWORD = config.get('transcripts_password')