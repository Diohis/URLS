from aiogram.filters import BaseFilter
from aiogram.types import Message

class URLFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        print("http://" in message.text)
        print("https://" in message.text)
        return "http://" in message.text or "https://" in message.text