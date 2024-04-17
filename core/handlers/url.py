import string
import random
import qrcode
import datetime
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from calendar import monthrange

from aiogram import Router, types, F, Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto, InputMedia
from aiogram.fsm.state import StatesGroup, State

from core.settings import settings,worksheet_urls
from core.database.Table import *
from core.keyboards.inline import *
from core.filters.Filters import URLFilter
from core.message.text import get_text_start_mess

router = Router()


class UrlState(StatesGroup):
    name = State()
    url = State()
    last_message_id = ()


'''    x_day = [i for i in range(1,25)]
    y_day = [i*0 for i in range(1,25)]
    x_month=[i for i in range(1,days+1)]
    y_month=[i*0 for i in range(1,days+1)]
    x_year=[i for i in range(1,13)]
    y_year=[i*0 for i in range(1,13)]

    y_day[i.time.hour - 1] += 1
    y_month[i.time.day - 1] += 1
    y_year[i.time.month - 1] += 1

    day = dict(visits = y_day,time = x_day)
    month = dict(visits=y_month, time=x_month)
    year = dict(visits=y_month, time=x_month)
    all = [day, month, year]'''


# ===================================Верификация курьера===================================
@router.callback_query(UrlKeyboard.filter(F.action == "stats"))
async def url_stats(callback: types.CallbackQuery, callback_data: UrlKeyboard, bot: Bot):
    urls = await table_url.get(user_id=callback.from_user.id)
    if urls==None:
        await callback.answer("У вас еще нет сокращенных ссылок!")
        return
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text="Выберите нужную вам ссылку для просмотра статистики",
                                         reply_markup=create_statistics_buttons(urls))

    else:
        await callback.message.edit_text(text="Выберите нужную вам ссылку для просмотра статистики",
                                     reply_markup=create_statistics_buttons(urls))


@router.callback_query(UrlKeyboard.filter(F.action == "create"))
async def url_create(callback: types.CallbackQuery, callback_data: UrlKeyboard, state: FSMContext):
    await callback.message.edit_text("Отправьте мне название для вашей ссылки.", reply_markup=cancel())
    await callback.answer()
    await state.set_state(UrlState.name)
    await state.update_data(last_message_id=callback.message.message_id)


@router.message(UrlState.name)
async def url_name(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["last_message_id"], reply_markup=None)
    await state.update_data(name=message.text)
    mess = await message.answer("Теперь отпавьте мне ссылку для сокращения.\nСсылка должна содержать <code>http://</code> или <code>https://</code>", reply_markup=cancel())
    await state.update_data(last_message_id=mess.message_id)
    await state.set_state(UrlState.url)


@router.message(UrlState.url, URLFilter())
async def url_url(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(url=message.text)
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data["last_message_id"], reply_markup=None)
    await state.clear()
    array_code = list(string.ascii_letters) + list(string.ascii_lowercase) + list("123456789")
    code = ""
    while True:
        for i in range(5):
            code += random.choice(array_code)
        if not (await table_url.get(code_url=code)):
            break
    new_url = {
        "name": data["name"],
        "base_url": data["url"],
        "code_url": code,
        "user_id": message.from_user.id
    }
    await table_url.create(new_url)
    url = f"{settings.url_server}?code={code}"

    img = qrcode.make(url)
    img.save(f"core/code/{code}.png")
    photo = FSInputFile(f"core/code/{code}.png")
    await bot.send_photo(message.chat.id, photo, caption=f"Ваша новая ссылка: \n<code>{url}</code>",
                         reply_markup=menu())
    # await message.answer(f")


@router.message(UrlState.url)
async def url_url_incorrectly(message: Message, state: FSMContext):
    await message.answer("Вы отправили некорректную ссылку.\nВ ссылке должно содержаться http:// или https://")


@router.callback_query(F.data == "showmenu")
async def show_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    is_admin = False
    if settings.bots.admin_id == callback.from_user.id:
        is_admin = True
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(get_text_start_mess(), reply_markup=create_start_buttons(is_admin))
    else:
        await callback.message.edit_text(get_text_start_mess(), reply_markup=create_start_buttons(is_admin))


@router.callback_query(UrlStat.filter())
async def url_create(callback: types.CallbackQuery, callback_data: UrlKeyboard, state: FSMContext):
    k = await table_redirects.get(code_url=callback_data.code)

    stat = f"Ссылка: {settings.url_server}?code={callback_data.code}\n"
    visits = 0
    visits_day = 0
    current_year = datetime.datetime.now().year
    month = int(datetime.date.today().month)  # int(input())
    days = monthrange(current_year, month)[1]

    if "tuple" not in str(type(k)):

        visits = 1
        visits_day = 1
        if k==None:
            visits = 0
            visits_day = 0
    else:
        visits = len(k)
        for i in k:
            if i.time.date() == datetime.datetime.now().date():
                visits_day += 1

    stat += "Общее количество переходов: " + str(visits) + "\n"
    stat += f"Количество переходов за сегодня: " + str(visits_day)
    keyboard = stat_time_buttons(code=callback_data.code)
    photo = FSInputFile(f"core/code/{callback_data.code}.png")
    if callback.message.photo:
        media = InputMediaPhoto(media=photo,caption=f"Статистика по ссылке с кодом {callback_data.code}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n{stat}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nВы можете посмотреть графики посещения или доп. статистику по кнопкам ниже.")
        await callback.message.edit_media(media=media,reply_markup=keyboard)
    else:
        await callback.message.delete()
        await callback.message.answer_photo(photo=photo,
                                        caption=f"Статистика по ссылке с кодом {callback_data.code}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n{stat}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nВы можете посмотреть графики посещения или доп. статистику по кнопкам ниже.",
                                        reply_markup=keyboard)


@router.callback_query(VisitsStat.filter(F.time == "day"))
async def url_create(callback: types.CallbackQuery, callback_data: UrlKeyboard, state: FSMContext):
    statistics = await table_redirects.get(code_url=callback_data.code)
    if statistics is None:
        await callback.answer("На данный момент нет статистики")
    x_day = [i for i in range(1, 25)]
    y_day = [i * 0 for i in range(1, 25)]
    current_year = datetime.datetime.now().year
    month = int(datetime.date.today().month)  # int(input())
    days = monthrange(current_year, month)[1]
    if "tuple" not in str(type(statistics)):
        y_day[statistics.time.hour - 1] += 1
    else:
        for i in statistics:
            y_day[i.time.hour - 1] += 1
    if sum(y_day) == 0:
        await callback.answer("На данный момент нет статистики")
    all = dict(посещения=y_day, часы=x_day)
    hrdf = pd.DataFrame(data=all)

    def plot():
        return sns.lineplot(x="часы", y="посещения", data=hrdf)

    with sns.axes_style('darkgrid'):
        # plt.subplot(211)
        fig = plt.figure(num=1, clear=True)
        figure = plot()
        plt.xticks(list(range(1, 25)))

        # Добавляем подписи к меткам
        plt.xlabel("Часы дня")
        plt.ylabel("Кол-во посещений")
        plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
        fig = figure.get_figure()
        fig.savefig(f"core/grafics/{callback_data.code}_day.png")
    # plt.grid(which="major", color="k")
    url = f"{settings.url_server}?code={callback_data.code}"
    text = f"График посещения ссылки\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nДиапазон: 1 день\nСсылка: {url}"
    media = InputMediaPhoto(media=FSInputFile(f"core/grafics/{callback_data.code}_day.png"),caption=text)
    await callback.message.edit_media(media=media,reply_markup=backtourlmenu(callback_data.code))


@router.callback_query(VisitsStat.filter(F.time == "month"))
async def url_create(callback: types.CallbackQuery, callback_data: UrlKeyboard, state: FSMContext):
    statistics = await table_redirects.get(code_url=callback_data.code)
    if statistics is None:
        await callback.answer("На данный момент нет статистики")
    current_year = datetime.datetime.now().year
    month = int(datetime.date.today().month)  # int(input())
    days = monthrange(current_year, month)[1]
    x_month = [i for i in range(1, days + 1)]
    y_month = [i * 0 for i in range(1, days + 1)]

    if "tuple" not in str(type(statistics)):
        y_month[statistics.time.day - 1] += 1
    else:
        for i in statistics:
            y_month[i.time.day - 1] += 1
    if sum(y_month) == 0:
        await callback.answer("На данный момент нет статистики")
    all = dict(посещения=y_month, часы=x_month)
    hrdf = pd.DataFrame(data=all)

    def plot():
        return sns.lineplot(x="часы", y="посещения", data=hrdf)

    with sns.axes_style('darkgrid'):
        # plt.subplot(211)
        fig = plt.figure(num=1, clear=True)
        figure = plot()

        plt.xticks(list(range(1, days+1)))

        # Добавляем подписи к меткам
        plt.xlabel("Дни месяца")
        plt.ylabel("Кол-во посещений")
        plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
        fig = figure.get_figure()
        fig.savefig(f"core/grafics/{callback_data.code}_month.png")
    # plt.grid(which="major", color="k")
    url = f"{settings.url_server}?code={callback_data.code}"
    text = f"График посещения ссылки\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nДиапазон: 1 месяц\nСсылка: {url}"
    media = InputMediaPhoto(media=FSInputFile(f"core/grafics/{callback_data.code}_month.png"), caption=text)
    await callback.message.edit_media(media=media, reply_markup=backtourlmenu(callback_data.code))


@router.callback_query(VisitsStat.filter(F.time == "year"))
async def url_create(callback: types.CallbackQuery, callback_data: UrlKeyboard, state: FSMContext):
    statistics = await table_redirects.get(code_url=callback_data.code)
    if statistics is None:
        await callback.answer("На данный момент нет статистики")
    x_year = [i for i in range(1, 13)]
    y_year = [i * 0 for i in range(1, 13)]

    if "tuple" not in str(type(statistics)):
        y_year[statistics.time.month - 1] += 1
    else:
        for i in statistics:
            y_year[i.time.month - 1] += 1
    if sum(y_year) == 0:
        await callback.answer("На данный момент нет статистики")
    all = dict(посещения=y_year, часы=x_year)
    hrdf = pd.DataFrame(data=all)

    def plot():
        return sns.lineplot(x="часы", y="посещения", data=hrdf)

    with sns.axes_style('darkgrid'):
        # plt.subplot(211)
        fig = plt.figure(num=1, clear=True)
        figure = plot()
        plt.xticks(list(range(1, 13)))

        # Добавляем подписи к меткам
        plt.xlabel("Месяца года")
        plt.ylabel("Кол-во посещений")
        plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
        fig = figure.get_figure()
        fig.savefig(f"core/grafics/{callback_data.code}_year.png")
    # plt.grid(which="major", color="k")
    url = f"{settings.url_server}?code={callback_data.code}"
    text = f"График посещения ссылки\n➖➖➖➖➖➖➖➖➖➖➖➖➖\nДиапазон: 1 год\nСсылка: {url}"
    media = InputMediaPhoto(media=FSInputFile(f"core/grafics/{callback_data.code}_year.png"),caption=text)
    await callback.message.edit_media(media=media,reply_markup=backtourlmenu(callback_data.code))

@router.callback_query(AnyData.filter())
async def show_anydata(callback:CallbackQuery, callback_data:AnyData):
    statistics = await table_redirects.get(code_url=callback_data.code)
    browser = {}
    os = {}
    device ={}
    if statistics==None:
        await callback.answer("На данный момент нет статистики")
        return
    if "tuple" not in str(type(statistics)):
        pass
    else:
        for i in statistics:
            if i.browser not in browser:
                browser[i.browser] =1
            else:
                browser[i.browser] += 1
            if i.os not in os:
                os[i.os] =1
            else:
                os[i.os] += 1
            if i.device not in device:
                device[i.device] =1
            else:
                device[i.device] += 1

    text = f"Статистика по ссылке с кодом {callback_data.code}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    text+="╭🌐 <b>Браузеры:</b>\n"
    n = 0
    for key,value in browser.items():
        symbol = ""
        end = ""
        if n==len(browser)-1:
            symbol = "╰"
        else:
            symbol = "├"
            end = "\n"
        text += f"{symbol} <b>{key} -> {value}</b>{end}"
        n+=1
    text+="\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    text+="╭💻 <b>Операционные системы:</b>\n"
    n = 0
    for key, value in os.items():
        symbol = ""
        end = ""
        if n == len(os) - 1:
            symbol = "╰"
        else:
            symbol = "├"
            end ="\n"
        text += f"{symbol} <b>{key} -> {value}</b>{end}"
        n += 1
    text += "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    text += "╭📱 <b>Устройства:</b>\n"
    n = 0
    for key, value in device.items():
        symbol = ""
        end = ""
        if n == len(device) - 1:
            symbol = "╰"
        else:
            symbol = "├"
            end ="\n"
        text += f"{symbol} <b>{key} -> {value}</b>{end}"
        n += 1
    await callback.message.edit_caption(caption=text,reply_markup=backtourlmenu(callback_data.code))

@router.callback_query(F.data == "load_google")
async def show_google(callback: types.CallbackQuery):
    records= await table_user.get("user_id","username")
    msg = await callback.message.answer("Подождите, сейчас бот выгрузит информацию")
    worksheet_urls.clear()
    worksheet_urls.insert_row(["user_id","username","Количество ссылок","Количество переходов"],1)
    users = []
    for i in records:
        user = [i.user_id,i.username]
        n_url = 0
        n_redirect = 0
        url = await table_url.get(user_id = i.user_id)
        if url:
            n_url = len(url)
            if (n_url):
                for j in url:
                    k_url = await table_redirects.get(code_url = j.code_url)
                    if(k_url):
                        n_redirect += len(k_url)

        user.append(n_url)
        user.append(n_redirect)
        users.append(user)
    for k,i in enumerate(users):
        worksheet_urls.insert_row(i,index=k+2)
    await msg.edit_text(text="Выгрузка информации завершена!\n Таблица пользователей: https://docs.google.com/spreadsheets/d/1w1dXO2JqLDe23Tn6EFNE8laYATsgT59_oD4VZ4T2CAA")
    await callback.answer()