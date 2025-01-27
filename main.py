import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from food import get_food_info
from weather import get_current_weather
from config import weather_url, weather_key


bot = Bot(token="7206703634:AAF93vZytKvBTMWexu34HG8HaAvUpxcEKMw")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    name = State()
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    goal = State()
    water = State()
    food = State()
    workout = State()

user_info = {}
user_water_intake = {}
user_food_log = {}
user_workout = {}
base_norm = {}


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.")


@dp.message(Command("set_profile"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Как вас зовут?")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Сколько вам лет? (полных)")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Какой у вас вес? (в кг)")
    await state.set_state(Form.weight)


@dp.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Какой у вас рост? (в см)")
    await state.set_state(Form.height)


@dp.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply("Сколько минут в день вы уделяете спорту?")
    await state.set_state(Form.activity)


@dp.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    await state.update_data(activity=message.text)
    await message.reply("В каком городе вы проживаете?")
    await state.set_state(Form.city)


@dp.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.reply("Ваша цель по потреблению калорий в день?")
    await state.set_state(Form.goal)


@dp.message(Form.goal)
async def process_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)

    user_data = await state.get_data()

    response_message = (
        f"Ваш профиль создан:\n"
        f"Имя: {user_data['name']}\n"
        f"Возраст: {user_data['age']}\n"
        f"Вес: {user_data['weight']} кг\n"
        f"Рост: {user_data['height']} см\n"
        f"Спорт (минут в день): {user_data['activity']}\n"
        f"Город: {user_data['city']}\n"
        f"Цель по калориям: {user_data['goal']}"
    )

    user_id = message.from_user.id
    if user_id not in user_info:
        user_info[user_id] = {
            "name": user_data['name'],
            "age": int(user_data['age']),
            "weight": float(user_data['weight']),
            "height": float(user_data['height']),
            "activity": int(user_data['activity']),
            "city": user_data['city'],
            "goal": float(user_data['goal'])
        }

    await message.reply(response_message)
    await state.clear()



@dp.message(Command("log_water"))
async def cmd_log_water(message: types.Message, state: FSMContext):
    await state.set_state(Form.water)
    await message.reply("Сколько выпили воды? Пожалуйста, введите количество в миллилитрах.")


@dp.message(Form.water)
async def process_water_input(message: types.Message, state: FSMContext):
    try:
        water_amount = int(message.text)

        user_id = message.from_user.id
        data = await state.get_data()

        if user_id in user_water_intake:
            user_water_intake[user_id] += water_amount
        else:
            user_water_intake[user_id] = water_amount

        total_water = user_water_intake[user_id]
        await message.reply(f"Вы добавили {water_amount} мл воды. Всего: {total_water} мл.")

    except ValueError:
        await message.reply("Пожалуйста, введите корректное число.")

    await state.clear()


@dp.message(Command("log_food"))
async def cmd_log_food(message: types.Message, state: FSMContext):
    await state.set_state(Form.food)
    await message.reply("Введите название продукта:")


@dp.message(Form.food)
async def process_food_name(message: types.Message, state: FSMContext):
    food_name = message.text
    product_data = await get_food_info(food_name)

    if product_data:
        product_name = product_data['foods'][0]['food_name']
        calories = float(product_data['foods'][0]['nf_calories'])

        user_id = message.from_user.id
        if user_id in user_food_log:
            user_food_log[user_id] += calories
        else:
            user_food_log[user_id] = calories

        await message.reply(f"Вы добавили продукт: {product_name} Калорийность: {calories}")

    else:
        await message.reply("Продукт не найден. Попробуйте ввести другое название.")

    await state.clear()


@dp.message(Command("log_workout"))
async def cmd_log_workout(message: types.Message, state: FSMContext):
    await state.set_state(Form.workout)
    await message.reply("Введите чем и сколько минут сегодня занимались спортом")

@dp.message(Form.workout)
async def process_workout(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    workout = (message.text).split(" ")[-1]
    type = (message.text).split(" ")[0]

    workout = int(workout)

    print(workout, type)
    print(user_info[user_id])

    if user_id in user_workout:
        user_workout[user_id] += (workout / 30) * 200
    else:
        user_workout[user_id] = (workout / 30) * 200

    await message.reply(f"{type} {workout} минут — 300 ккал. Дополнительно: выпейте 200 мл воды.")

    await state.clear()

@dp.message(Command("log_base_norm"))
async def cmd_log_base_norm(message: types.Message, state: FSMContext):

    user_id = message.from_user.id


    temp = get_current_weather(weather_key, weather_url,  user_info[user_id]['city'])

    if temp > 25:
        formula_water = user_info[user_id]['weight'] * 30 + 500 * user_info[user_id]['activity'] / 30 - 1000
    else:
        formula_water = user_info[user_id]['weight'] * 30 + 500 * user_info[user_id]['activity'] / 30

    formula_food = 10 * user_info[user_id]['weight'] + 6.25 * user_info[user_id]['height'] - 5 * user_info[user_id]['age']

    base_norm[user_id] = [formula_water, formula_food]


    await message.reply(f"Нужно потреблять {formula_water} воды в мл и {formula_food} калорий")



@dp.message(Command("check_progress"))
async def cmd_log_progress(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    water_cons = user_water_intake[user_id]
    workout = user_workout[user_id]
    food_cons = user_food_log[user_id]

    water_must = base_norm[user_id][0]
    food_must = base_norm[user_id][1]

    await message.reply(f"Прогресс: \n"
                        f" Вода: \n"
                        f" -Выпито: {water_cons} мл из {water_must} \n"
                        f" -Осталось: {water_must - float(water_cons)} \n"
                        
                        f" Калории: \n"
                        f" - Потреблено: {food_cons} ккал из {food_must} \n"
                        f" - Сожжено: {workout} ккал.")





async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())