# Обработчики Telegram Бота (Handlers)

Эта папка содержит логику взаимодействия бота с пользователем-кандидатом.

## 🛠 Технологии
- `python-telegram-bot` (v20+)
- `ConversationHandler` (машина состояний для пошагового сбора данных)
- Базовые модули `telegram.ext` (`CommandHandler`, `MessageHandler`, `CallbackQueryHandler`)

## 📂 Файлы и их назначение
1. **`start.py`**: Обработка команды `/start`. Бот приветствует пользователя, проверяет по его `telegram_id` наличие записи в таблице `employees` базы Supabase. Если он уже есть, предлагает редактирование; если нет — начинает регистрацию.
2. **`registration.py`**: Сердце бота. Огромный `ConversationHandler`, состоящий из 7-ми шагов (FIO, Phone, Age, District, Experience, Specialization, Portfolio).
   - В конце флоу (`DONE` стейт), бот формирует словарь данных и отправляет его через `supabase.client.table("employees").insert().execute()`.

## 💡 Для ИИ Агентов
Если нужно добавить новый вопрос в анкету:
1. Добавьте новый константный стейт в `registration.py` (например, `NEW_QUESTION_STATE = range(X)`).
2. Поправьте цепочку переходов (`return NEXT_STATE`) внутри функций-обработчиков.
3. Добавьте текстовое поле в базу `supabase/migrations/001_init.sql`.
