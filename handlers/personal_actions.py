from random import choice

import structlog
import ujson
from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from fluent.runtime import FluentLocalization

from fluent_loader import get_fluent_localization
from utils import generate_tarot_reading

# Declare router
router = Router()
router.message.filter(F.chat.type == "private")

# Declare logger
logger = structlog.get_logger()

LANGUAGES = {
    "Українська": "uk",
    "English": "en",
    "Русский": "ru",
}


with open('tarot_cards.json', 'r') as file:
    TAROT_CARDS = ujson.load(file)


def get_image_url(image):
    return f"https://your-s3-bucket.s3.amazonaws.com/{image}"


async def language_keyboard(message: Message, l10n: FluentLocalization):
    builder = ReplyKeyboardBuilder()
    for lang in LANGUAGES.keys():
        builder.add(KeyboardButton(text=lang))
    await message.answer(
        l10n.format_value("hello-msg"),
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


# Declare handlers
@router.message(Command("start"))
async def start(message: Message, l10n: FluentLocalization):
    await language_keyboard(message=message, l10n=l10n)


@router.message(lambda message: message.text in LANGUAGES)
async def language_selection(message: Message, state: FSMContext):
    language_code = LANGUAGES[message.text]
    await state.update_data(language_code=language_code)

    l10n = get_fluent_localization(language_code)
    # await state.finish()  # Завершуємо попередній стан, якщо він був
    await message.answer(
        l10n.format_value("selected-language")
    )


# Хендлер для обробки текстових повідомлень (запитів користувача)
@router.message(F.text)
async def tarot_reading(message: Message, state: FSMContext, l10n: FluentLocalization):
    user_question = message.text
    card, image = choice(list(TAROT_CARDS.items()))
    get_image_url(image)

    data = await state.get_data()
    language_code = data.get("language_code")
    print(f"language_code: {language_code}")
    # Перевірка на наявність language_code
    if not language_code:
        # Створюємо клавіатуру для вибору мови
        await language_keyboard(message=message, l10n=l10n)
        return  # Завершуємо функцію, щоб чекати на вибір мови

    # Генерація тексту для відповіді на основі запиту
    tarot_reading = generate_tarot_reading(user_question, card, language_code)

    image_url = "https://pottertaro.s3.eu-central-1.amazonaws.com/2024-10-24%2017.40.11.jpg?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEG8aDGV1LWNlbnRyYWwtMSJGMEQCICo45nqpROyNVSTXcqnTQNs%2FOJnHtGoFzO2evOUoO%2FreAiB21YOIgddhOO154GQOaEgLOxPZcxBue%2FPjjHqqH9QB3irxAgjY%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAAaDDk3NTA1MDM1OTc0MCIMF8YOhd2HzPnsec9SKsUC5U51%2FPTM%2BaA4ja81Fg7A0VCNS8%2Btw03xBHlNhXhWWpavh3SEPblQgLs%2BFTwZuKB8oo%2BfgPW4VoA%2Fc7YDcbyXV%2FtkwR98o6XIonHthnecELoAKDKA3nxQpKGTtcRssSLx0A%2BcLokucEPjDcS4EdxpjLtAUVehFvmgSIdyG4IYN1d1TBwYnWGIdfuJdzraHhdTtiZj2U0RpJdrQZP9NHcIUMzY0y9TsSupT%2FyGMVeQVHV4PwOVehEzEJWQyT60xJaejQG7heMo8zfLUMcjjNR9q0Gup1rUjIQfK0Bt0ehs5mD2iSkJ2dMAQ54vBmRbAJ4nPeIjqaOlTiypc36y7kGX%2BWVWw%2B94I1Bjt7Z70TSCcS9wefsBwupe1WXjDofA5n%2BYZA369oGzPB0trjFfSMavZZg%2BB%2FUZBbofQEJYs%2Fl2yNEKYMGDzTD%2Ft%2Bm4Bjq0Au%2FBhrZWZly7k3WAYFlZ2EmhqAgstaDLo%2BI7Sq5P3C26dQASomDYsqSxqDQqUORIuMFXeYYnSsLpLGWFzLtsf6xfxjs%2FAGCdzpAhXSD167BcD9x2f1gd8xn76rp11uMx%2FWKXA%2F%2BQ5dhzgVoAknxG7AynChG%2BI0wi38%2F2OgLHs3tZe242Gf6ne6kgZt%2FURPNiXHym31NaMgd0imSnnz0fs9DyrfYLKSK0rEJnl28eR7dOZYzUBORjo9r7jUUJ9Rje4hHNX7vamEqdHUIqokLEcvmnQIgQuPr22uQKKsSfN8g70Ze2UNVqgeFQnjeup0waBXT3P%2FrB%2Bq0fvBN%2Fr%2FnvmyOk5qlKjPsn1%2BbuC20V59r18sv31oGfqS3kOzRyJl1p7I1e3Xc7pBVsIKxsafnuSlZNZFpV&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241024T145001Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIA6GBMHYO6GF6EQC7L%2F20241024%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=14684c2129deb52fb9e17a4a18831c11b58e298353c0d416afbcd8138e8f37ac"
    # Відправлення фото карти, якщо воно доступне
    if image_url:
        await message.answer_photo(photo=image_url, caption=f"<b>{card}</b>")

    # Відправлення текстового пояснення
    await message.answer(tarot_reading, parse_mode=ParseMode.HTML)
