from os import environ
from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=environ.get("OPENAI_API_KEY"))


def remove_prefix(text, prefix):
    if text.lower().startswith(prefix.lower()):
        return text[len(prefix):]
    return text  # or whatever


def generate_tarot_reading(user_query: str, card: str, language_code: str):
    # prompt = (
    #     f"У вас є вибрана карта Таро: '{card}'. "
    #     f"Вам потрібно дати трактування цієї карти в контексті запиту: '{user_query}'. "
    #     "Опишіть значення карти, її вплив на ситуацію та які поради вона може дати у відповідь на запит."
    # )
    prompt = f"""You have drawn the Tarot card: '{card}'. You need to interpret this card in the context of the 
    question: '{user_query}'. Describe the meaning of the card, its impact on the situation, and any advice it might 
    offer in response to the question. Respond in {language_code}.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты профессиональный гадатель на картах Таро."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7  # Регулюємо креативність відповіді
    )

    reading = response.choices[0].message.content
    print(type(reading))
    print(reading)
    return reading
