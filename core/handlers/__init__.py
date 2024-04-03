from aiogram import Router


from .basic import router as bas
from .url import router as url

main_router = Router()

main_router.include_routers(url,bas)