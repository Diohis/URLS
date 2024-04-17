# pip install environs
# import gspread
import os
from environs import Env
from dataclasses import dataclass
import gspread
from google.oauth2.service_account import Credentials
# Путь от корня системы до папки core например:
# D:\Programing\Flow_Work\core
home = os.path.dirname(__file__)

@dataclass
class Bots:
    bot_token: str
    admin_id: int

@dataclass
class Settings:
    bots: Bots
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    url_server:str

def get_settings(path: str):
    evn = Env()
    evn.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=evn.str("BOT_TOKEN"),
            admin_id=evn.int("ADMIN_ID"),
        ),
        db_user=evn.str("DB_USER"),
        db_password=evn.str("DB_PASSWORD"),
        db_host=evn.str("DB_HOST"),
        db_port=evn.str("DB_PORT"),
        db_name=evn.str("DB_NAME"),
        url_server = evn.str("URL_SERVER")
    )

settings = get_settings('config')
scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(f'{home}/cred.json')
client = gspread.authorize(credentials.with_scopes(scope))
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1w1dXO2JqLDe23Tn6EFNE8laYATsgT59_oD4VZ4T2CAA/edit#gid=0')
worksheet_urls = sheet.worksheet('urls')
