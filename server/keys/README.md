# Finik Keys

- `finik_private.pem` — наш приватный ключ. Никому не отправлять.
- `finik_public.pem` — наш публичный ключ. Именно этот файл нужно отправить в `finik@quickpay.kg`.

Важно:
- `FENIK_PRIVATE_KEY_PATH` в сервере должен указывать на `finik_private.pem`.
- `FENIK_PUBLIC_KEY_PATH` не нужно заполнять нашим ключом. Это поле потом предназначено для публичного ключа самого Finik, если они пришлют его для проверки webhook-подписи.
