from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters.callback_data import CallbackData

class UrlKeyboard(CallbackData, prefix="url"):
    action:str
class UrlStat(CallbackData, prefix="stat"):
    code:str
class VisitsStat(CallbackData, prefix="visits"):
    time:str
    code:str
class AnyData(CallbackData, prefix="anydata"):
    code:str

def create_start_buttons() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Статистика", callback_data=UrlKeyboard(action="stats").pack()),
         InlineKeyboardButton(text="Сократить ссылку",callback_data=UrlKeyboard(action="create").pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cancel()->InlineKeyboardMarkup:
    button = [[
        InlineKeyboardButton(text = "Отмена", callback_data="showmenu")
    ]]
    return InlineKeyboardMarkup(inline_keyboard=button)
def menu()->InlineKeyboardMarkup:
    button = [[
        InlineKeyboardButton(text = "Меню", callback_data="showmenu")
    ]]
    return InlineKeyboardMarkup(inline_keyboard=button)

def create_statistics_buttons(urls)->InlineKeyboardMarkup:
    all_buttons = []
    buttons = []
    if "tuple" not in str(type(urls)):
        all_buttons.append([InlineKeyboardButton(text=urls.name, callback_data=UrlStat(code=urls.code_url).pack())])
    else:
        for i in urls:
            buttons.append(InlineKeyboardButton(text=i.name, callback_data=UrlStat(code=i.code_url).pack()))
            if len(buttons)==3:
                all_buttons.append(buttons)
                buttons=[]
    all_buttons.append(buttons)
    all_buttons.append([InlineKeyboardButton(text="Назад", callback_data="showmenu")])
    return InlineKeyboardMarkup(inline_keyboard=all_buttons)

def stat_time_buttons(code:str)->InlineKeyboardMarkup:
    buttons = []
    buttons.append([
    InlineKeyboardButton(text="За день", callback_data=VisitsStat(time="day",code=code).pack()),
    InlineKeyboardButton(text="За месяц", callback_data=VisitsStat(time="month",code=code).pack()),
    InlineKeyboardButton(text="За год", callback_data=VisitsStat(time="year",code=code).pack()),
    ])
    buttons.append([InlineKeyboardButton(text="Другие данные",callback_data=AnyData(code=code).pack())])
    buttons.append([
        InlineKeyboardButton(text="Назад",callback_data=UrlKeyboard(action="stats").pack())
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
def backtourlmenu(code:str)->InlineKeyboardMarkup:
    button =[[
        InlineKeyboardButton(text="Назад",callback_data=UrlStat(code=code).pack())
    ]]
    return InlineKeyboardMarkup(inline_keyboard=button)