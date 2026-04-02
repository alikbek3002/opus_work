import re
import os

file_path = "bot/handlers/registration.py"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update text for Experience
text = text.replace('f"💼 Где работали', 'f"💼 Опыт работы')

# 2. Add photo text
text = text.replace(
    'Шаг 4/13: Сделайте селфи прямо сейчас на фронтальную камеру, чтобы было четко видно ваше лицо, и отправьте мне:',
    'Шаг 4/13: Сделайте фото для анкеты или вставьте из галереи. Анкеты с фото открываются на 70% чаще!'
)

# 3. Remove Telegram username from build_summary
lines = text.split('\n')
lines = [l for l in lines if 'Telegram username:' not in l]
lines = [l for l in lines if 'Есть рекомендации:' not in l]
text = '\n'.join(lines)

# 4. Remove Recommendations step
text = text.replace('    HAS_RECOMMENDATIONS,\n', '')
text = text.replace('= range(15)', '= range(14)')

text = text.replace(
'''    if field == "has_recommendations":
        await query.message.reply_text(
            "Есть рекомендации от прошлых работодателей?",
            reply_markup=build_reply_keyboard(YES_NO_OPTIONS),
        )
        return HAS_RECOMMENDATIONS\n\n''', '')

text = text.replace('            InlineKeyboardButton("⭐ Рекомендации", callback_data="edit_field:has_recommendations"),\n', '')

text = re.sub(r'async def recommendations_handler.*?return CONTACT_METHOD\n', '', text, flags=re.DOTALL)

text = text.replace(
'''    await update.message.reply_text(
        "Шаг 11/13: Есть рекомендации от прошлых работодателей?",
        reply_markup=build_reply_keyboard(YES_NO_OPTIONS),
    )
    return HAS_RECOMMENDATIONS''',
'''    await update.message.reply_text(
        "Шаг 12/12: Выберите способ связи по номеру:",
        reply_markup=build_reply_keyboard(CONTACT_METHOD_OPTIONS),
    )
    return CONTACT_METHOD'''
)

text = re.sub(r'\s*HAS_RECOMMENDATIONS: \[MessageHandler.*?\],', '', text, flags=re.DOTALL)

# Steps recalculation: replace "Шаг \d+/13" with "Шаг \1/12"
text = re.sub(r"Шаг (\d+)/13", r"Шаг \1/12", text)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Patch applied for text updates!")
