# Finik Keys

- `finik_private.pem` — наш приватный ключ. Никому не отправлять.
- `finik_public.pem` — наш публичный ключ. Именно этот файл нужно отправить в `finik@quickpay.kg`.

Важно:
- `FINIK_PRIVATE_KEY_PATH` в сервере должен указывать на `finik_private.pem`.
- `FINIK_PUBLIC_KEY_PATH` не нужно заполнять нашим ключом. Это поле потом предназначено для публичного ключа самого Finik, если они пришлют его для проверки webhook-подписи.
- Для Railway надёжнее задавать `FINIK_PRIVATE_KEY` или `FINIK_PRIVATE_KEY_BASE64` через Variables, потому что `.pem` файлы не коммитятся в репозиторий.
