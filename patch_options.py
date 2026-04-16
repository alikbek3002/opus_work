import os
import re

file_path = "bot/handlers/registration.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace DISTRICT_OPTIONS array
text = re.sub(
    r'DISTRICT_OPTIONS = \[.*?\]',
    '''DISTRICT_OPTIONS = [
    "Бишкек (весь город)",
    "ЦУМ",
    "Бишкек Парк",
    "Филармония",
    "Моссовет",
    "Ош базар",
    "Аламединский рынок",
    "Тунгуч",
    "Микрорайоны",
    "7 мкр",
    "12 мкр",
    "Учкун мкр",
    "Джал",
    "Южный Магистраль",
    "Кызыл-Аскер",
    "Ак-Ордо",
    "Ак-Орго",
    "Ала-Тоо",
    "Дордой",
    "Дордой-1",
    "Аламедин-1",
    "Лебединовка",
    "Кок-Джар",
    "Орто-Сай",
    "Орто-Сай село",
    "Чон-Арык",
    "Нижняя Ала-Арча",
    "Новопавловка",
    "Новопокровка",
    "Пригородное",
    "Военно-Антоновка",
    "Байтик",
]''',
    text,
    flags=re.DOTALL
)

# Replace SPECIALIZATION_OPTIONS
text = re.sub(
    r'SPECIALIZATION_OPTIONS = \[.*?\]',
    '''SPECIALIZATION_OPTIONS = [
    "Официант",
    "Повар универсал",
    "Кухработник",
    "Уборщица/Техничка",
    "Посудомойщица",
    "Бармен",
    "Продавец-консультант",
    "Кассир",
    "Грузчик",
    "Помощник повара",
    "Клинер",
]''',
    text,
    flags=re.DOTALL
)

# Add ReplyKeyboardRemove for photo -> specializations
if "reply_markup=ReplyKeyboardRemove()" not in text.split("Шаг 5/13:")[0][-80:]:
    text = text.replace(
        '''    await update.message.reply_text(
        "Шаг 5/13: Кем хотите работать? Можно выбрать несколько вариантов:",
        reply_markup=build_multiselect_inline_keyboard(SPECIALIZATION_OPTIONS, set(), "spec"),
    )''',
        '''    from telegram import ReplyKeyboardRemove
    await update.message.reply_text("Отлично! 📸", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        "Шаг 5/13: Кем хотите работать? Можно выбрать несколько вариантов:",
        reply_markup=build_multiselect_inline_keyboard(SPECIALIZATION_OPTIONS, set(), "spec"),
    )'''
    )

# Add ReplyKeyboardRemove for experience -> district
text = text.replace(
    '''    await update.message.reply_text(
        "Шаг 7/13: В каких районах готовы работать? Можно выбрать несколько:",
        reply_markup=build_multiselect_inline_keyboard(DISTRICT_OPTIONS, set(), "dist"),
    )''',
    '''    from telegram import ReplyKeyboardRemove
    await update.message.reply_text("Принято.", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        "Шаг 7/13: В каких районах готовы работать? Можно выбрать несколько:",
        reply_markup=build_multiselect_inline_keyboard(DISTRICT_OPTIONS, set(), "dist"),
    )'''
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Registration options patched successfully!")
