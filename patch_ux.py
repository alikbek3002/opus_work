import os

file_path = "bot/handlers/registration.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Modify build_reply_keyboard to add "Пропустить"
if "rows + [[\"Пропустить\"]]" not in text:
    text = text.replace(
        'return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)',
        'return ReplyKeyboardMarkup(rows + [["Пропустить"]], resize_keyboard=True, one_time_keyboard=True)'
    )

# Add "Пропустить" to specific questions
text = text.replace(
    'reply_markup=ReplyKeyboardRemove(),\n    )\n    return AGE',
    'reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True, one_time_keyboard=True),\n    )\n    return AGE'
)

text = text.replace(
    'reply_markup=ReplyKeyboardRemove(),\n    )\n    return PHOTO',
    'reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True, one_time_keyboard=True),\n    )\n    return PHOTO'
)

text = text.replace(
    'reply_markup=ReplyKeyboardRemove(),\n    )\n    return ABOUT_ME',
    'reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True, one_time_keyboard=True),\n    )\n    return ABOUT_ME'
)

# Allow skipping in age_handler:
text = text.replace(
    'if not text.isdigit() or int(text) < 14 or int(text) > 100:',
    'if text == "Пропустить":\n        context.user_data["age"] = None\n    elif not text.isdigit() or int(text) < 14 or int(text) > 100:'
)
text = text.replace(
    'context.user_data["age"] = int(text)',
    'if text != "Пропустить":\n        context.user_data["age"] = int(text)'
)

# Allow skipping in photo_handler
photo_logic = """    photos = update.message.photo or []

    if not photos:
        await update.message.reply_text("⚠️ Пожалуйста, отправьте фото именно как изображение.")
        return PHOTO

    context.user_data["photo_file_id"] = photos[-1].file_id"""

new_photo_logic = """    if update.message.text and update.message.text.strip() == "Пропустить":
        context.user_data["photo_file_id"] = None
    else:
        photos = update.message.photo or []
        if not photos:
            await update.message.reply_text("⚠️ Пожалуйста, отправьте фото именно как изображение.")
            return PHOTO
        context.user_data["photo_file_id"] = photos[-1].file_id"""
text = text.replace(photo_logic, new_photo_logic)

# Options checking
text = text.replace('not in EXPERIENCE_OPTIONS:', 'not in EXPERIENCE_OPTIONS and experience != "Пропустить":')
text = text.replace('not in GENDER_OPTIONS:', 'not in GENDER_OPTIONS and gender != "Пропустить":')
text = text.replace('not in SCHEDULE_OPTIONS:', 'not in SCHEDULE_OPTIONS and answer != "Пропустить":')
text = text.replace('not in SANITARY_BOOK_OPTIONS:', 'not in SANITARY_BOOK_OPTIONS and answer != "Пропустить":')
text = text.replace('not in YES_NO_OPTIONS:', 'not in YES_NO_OPTIONS and answer != "Пропустить":')
text = text.replace('not in CONTACT_METHOD_OPTIONS:', 'not in CONTACT_METHOD_OPTIONS and method != "Пропустить":')

# Options assigning
text = text.replace('context.user_data["gender"] = gender\n', 'context.user_data["gender"] = gender if gender != "Пропустить" else None\n')
text = text.replace('context.user_data["experience"] = experience\n', 'context.user_data["experience"] = experience if experience != "Пропустить" else None\n')
text = text.replace('context.user_data["schedule"] = answer\n', 'context.user_data["schedule"] = answer if answer != "Пропустить" else None\n')
text = text.replace('context.user_data["has_sanitary_book"] = answer\n', 'context.user_data["has_sanitary_book"] = answer if answer != "Пропустить" else None\n')
text = text.replace('context.user_data["has_recommendations"] = answer == "Да"', 'context.user_data["has_recommendations"] = (answer == "Да") if answer != "Пропустить" else None')
text = text.replace('context.user_data["has_whatsapp"] = method == "WhatsApp"', 'context.user_data["has_whatsapp"] = (method == "WhatsApp") if method != "Пропустить" else None')

# Multiselect logic
dist_block = """    if not selected:
        await query.answer("⚠️ Выберите хотя бы один район!", show_alert=True)
        return DISTRICT

    await query.answer()

    context.user_data["district"] = ", ".join(sorted(selected))"""
new_dist_block = """    await query.answer()
    context.user_data["district"] = ", ".join(sorted(selected)) if selected else None"""
text = text.replace(dist_block, new_dist_block)


spec_block = """    if not selected:
        await query.answer("⚠️ Выберите хотя бы одну профессию!", show_alert=True)
        return SPECIALIZATIONS

    await query.answer()

    context.user_data["specializations"] = ", ".join(sorted(selected))"""
new_spec_block = """    await query.answer()
    context.user_data["specializations"] = ", ".join(sorted(selected)) if selected else None"""
text = text.replace(spec_block, new_spec_block)


emp_block = """    if not selected:
        await query.answer("⚠️ Выберите хотя бы один формат!", show_alert=True)
        return EMPLOYMENT_TYPE

    await query.answer()
    context.user_data["employment_type"] = ", ".join(sorted(selected))"""
new_emp_block = """    await query.answer()
    context.user_data["employment_type"] = ", ".join(sorted(selected)) if selected else None"""
text = text.replace(emp_block, new_emp_block)


about_me_block = """    if len(about_me) < 20:
        await update.message.reply_text("⚠️ Напишите чуть подробнее (желательно 2-3 предложения).")
        return ABOUT_ME

    context.user_data["about_me"] = about_me"""
new_about_me = """    if about_me == "Пропустить":
        context.user_data["about_me"] = None
    elif len(about_me) < 20:
        await update.message.reply_text("⚠️ Напишите чуть подробнее (желательно 2-3 предложения).")
        return ABOUT_ME
    else:
        context.user_data["about_me"] = about_me"""
text = text.replace(about_me_block, new_about_me)

# Confirm registration try catch error retry
confirm_block = """    try:
        employee = save_employee(employee_data)
    except Exception as e:
        error_text = str(e)
        if "PGRST204" in error_text:
            await query.edit_message_text(
                "❌ База данных ещё не обновлена под новую анкету.\\n"
                "Нужно применить миграцию: `supabase/migrations/015_add_sanitary_book.sql` в SQL Editor Supabase и повторить отправку."
            )
            context.user_data.clear()
            return ConversationHandler.END
        else:
            await query.edit_message_text(f"❌ Произошла ошибка при сохранении анкеты: {error_text}")
            context.user_data.clear()
            return ConversationHandler.END"""

new_confirm_block = """    try:
        employee = save_employee(employee_data)
    except Exception as e:
        error_text = str(e)
        err_msg = f"❌ Произошла ошибка при сохранении анкеты: {error_text}"
        if "PGRST204" in error_text:
            err_msg = "❌ База данных ещё не обновлена под новую анкету.\\nНужно применить миграцию: `supabase/migrations/015_add_sanitary_book.sql` в SQL Editor Supabase."
        
        await query.edit_message_text(
            err_msg + "\\n\\nПодтвердите повторную отправку:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Повторить отправку", callback_data="confirm_registration")]])
        )
        return CONFIRM"""
text = text.replace(confirm_block, new_confirm_block)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Bot UX patches successfully applied!")
