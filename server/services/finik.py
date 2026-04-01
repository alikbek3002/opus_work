import base64
import binascii
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from config import settings


FINIK_PAYMENT_PATH = "/v1/payment"
DEFAULT_FINIK_MERCHANT_CATEGORY_CODE = "0742"
DEFAULT_FINIK_QR_NAME = "Opus"
DEFAULT_FINIK_REQUEST_TIMEOUT_SEC = 20


class FinikConfigError(RuntimeError):
    pass


class FinikRequestError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class FinikCreatePaymentResult:
    payment_url: str
    payment_status: str
    finik_payment_id: Optional[str] = None


def _normalize_pem(value: str) -> str:
    return value.strip().replace("\\n", "\n")


def _decode_base64_pem(value: Optional[str], label: str) -> Optional[str]:
    if not value:
        return None

    try:
        decoded = base64.b64decode(value).decode("utf-8").strip()
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise FinikConfigError(f"Некорректный base64 для {label}") from exc

    return _normalize_pem(decoded)


def _read_pem_value(value: Optional[str], path: Optional[str], label: str) -> str:
    if value:
        return _normalize_pem(value)

    if path:
        try:
            return Path(path).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise FinikConfigError(f"Не удалось прочитать {label}: {path}") from exc

    raise FinikConfigError(f"Не настроен {label}")


def _load_private_key():
    private_key_value = _decode_base64_pem(
        settings.FINIK_PRIVATE_KEY_BASE64,
        "приватного ключа Finik",
    ) or _read_pem_value(
        settings.FINIK_PRIVATE_KEY,
        settings.FINIK_PRIVATE_KEY_PATH,
        "приватный ключ Finik",
    )
    try:
        return serialization.load_pem_private_key(
            private_key_value.encode("utf-8"),
            password=None,
        )
    except Exception as exc:
        raise FinikConfigError("Некорректный приватный ключ Finik") from exc


def _load_public_key():
    if (
        not settings.FINIK_PUBLIC_KEY
        and not settings.FINIK_PUBLIC_KEY_BASE64
        and not settings.FINIK_PUBLIC_KEY_PATH
    ):
        return None

    public_key_value = _decode_base64_pem(
        settings.FINIK_PUBLIC_KEY_BASE64,
        "публичного ключа Finik",
    ) or _read_pem_value(
        settings.FINIK_PUBLIC_KEY,
        settings.FINIK_PUBLIC_KEY_PATH,
        "публичный ключ Finik",
    )
    try:
        return serialization.load_pem_public_key(public_key_value.encode("utf-8"))
    except Exception as exc:
        raise FinikConfigError("Некорректный публичный ключ Finik") from exc


def is_webhook_verification_configured() -> bool:
    return bool(
        settings.FINIK_PUBLIC_KEY
        or settings.FINIK_PUBLIC_KEY_BASE64
        or settings.FINIK_PUBLIC_KEY_PATH
    )


def build_webhook_url(base_url: str, payment_id: str) -> str:
    parts = urlsplit(base_url)
    query_params = parse_qsl(parts.query, keep_blank_values=True)
    query_params = [(key, value) for key, value in query_params if key != "payment_id"]
    query_params.append(("payment_id", payment_id))
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query_params), parts.fragment)
    )


def _canonicalize_headers(host: str, headers: Mapping[str, str]) -> str:
    x_api_headers: List[Tuple[str, str]] = []
    for key, value in headers.items():
        lower_key = key.lower()
        if lower_key.startswith("x-api-"):
            x_api_headers.append((lower_key, str(value).strip()))

    x_api_headers.sort(key=lambda item: item[0])
    parts = [f"host:{host}"]
    parts.extend(f"{key}:{value}" for key, value in x_api_headers)
    return "&".join(parts)


def _canonicalize_query(query_string: str) -> str:
    if not query_string:
        return ""

    pairs = parse_qsl(query_string, keep_blank_values=True)
    pairs.sort(key=lambda item: (item[0], item[1]))
    return "&".join(
        f"{quote(key, safe='')}={quote(value, safe='')}"
        for key, value in pairs
    )


def _canonicalize_json(body: Any) -> str:
    if body is None:
        return ""
    return json.dumps(body, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def build_signature_payload(
    *,
    http_method: str,
    path: str,
    host: str,
    headers: Mapping[str, str],
    query_string: str,
    body: Any,
) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    method = http_method.lower()
    canonical_headers = _canonicalize_headers(host, headers)
    canonical_query = _canonicalize_query(query_string)
    canonical_body = _canonicalize_json(body)

    payload = f"{method}\n{normalized_path}\n{canonical_headers}\n"
    if canonical_query:
        payload += f"{canonical_query}\n"
    payload += canonical_body
    return payload


def sign_payload(payload: str) -> str:
    private_key = _load_private_key()
    signature_bytes = private_key.sign(
        payload.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature_bytes).decode("utf-8")


def verify_payload_signature(payload: str, signature: str) -> bool:
    public_key = _load_public_key()
    if public_key is None:
        raise FinikConfigError("Проверка подписи включена, но публичный ключ Finik не задан")

    try:
        signature_bytes = base64.b64decode(signature, validate=True)
    except binascii.Error:
        return False

    try:
        public_key.verify(
            signature_bytes,
            payload.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


def verify_webhook_signature(
    *,
    http_method: str,
    path: str,
    query_string: str,
    headers: Mapping[str, str],
    body: Any,
    signature: str,
) -> bool:
    host = headers.get("host") or headers.get("Host")
    if not host:
        return False

    payload = build_signature_payload(
        http_method=http_method,
        path=path,
        host=host,
        headers=headers,
        query_string=query_string,
        body=body,
    )
    return verify_payload_signature(payload, signature)


def _extract_finik_error(
    response: requests.Response,
    response_json: Optional[Dict[str, Any]],
) -> str:
    if response_json:
        for key in ("ErrorMessage", "errorMessage", "message", "error"):
            value = response_json.get(key)
            if value:
                return str(value)
    text = response.text.strip()
    if text:
        return text[:500]
    return f"HTTP {response.status_code}"


def create_payment_link(
    *,
    payment_id: str,
    amount: int,
    redirect_url: str,
    webhook_url: str,
    description: Optional[str] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> FinikCreatePaymentResult:
    api_key = settings.FINIK_API_KEY
    account_id = settings.FINIK_ACCOUNT_ID
    mcc = DEFAULT_FINIK_MERCHANT_CATEGORY_CODE
    qr_name = DEFAULT_FINIK_QR_NAME
    base_url = settings.FINIK_API_BASE_URL.strip().rstrip("/")

    missing: List[str] = []
    if not api_key:
        missing.append("FINIK_API_KEY")
    if not account_id:
        missing.append("FINIK_ACCOUNT_ID")
    if not base_url:
        missing.append("FINIK_API_BASE_URL")
    if missing:
        raise FinikConfigError("Не хватает настроек Finik: " + ", ".join(missing))

    parsed_base = urlsplit(base_url)
    if parsed_base.scheme not in ("http", "https") or not parsed_base.netloc:
        raise FinikConfigError("Некорректный FINIK_API_BASE_URL")
    host = parsed_base.netloc

    timestamp = str(int(time.time() * 1000))

    data_payload: Dict[str, Any] = {
        "accountId": account_id,
        "merchantCategoryCode": mcc,
        "name_en": qr_name,
        "webhookUrl": webhook_url,
    }
    if description:
        data_payload["description"] = description
    if start_date is not None:
        data_payload["startDate"] = start_date
    if end_date is not None:
        data_payload["endDate"] = end_date

    payload: Dict[str, Any] = {
        "Amount": amount,
        "CardType": "FINIK_QR",
        "PaymentId": payment_id,
        "RedirectUrl": redirect_url,
        "Data": data_payload,
    }

    headers_to_sign = {
        "x-api-key": api_key,
        "x-api-timestamp": timestamp,
    }

    signature_payload = build_signature_payload(
        http_method="POST",
        path=FINIK_PAYMENT_PATH,
        host=host,
        headers=headers_to_sign,
        query_string="",
        body=payload,
    )
    signature = sign_payload(signature_payload)

    request_headers = {
        "Content-Type": "application/json",
        "Host": host,
        "x-api-key": api_key,
        "x-api-timestamp": timestamp,
        "signature": signature,
    }

    body_json = _canonicalize_json(payload)
    try:
        response = requests.post(
            f"{base_url}{FINIK_PAYMENT_PATH}",
            headers=request_headers,
            data=body_json.encode("utf-8"),
            allow_redirects=False,
            timeout=DEFAULT_FINIK_REQUEST_TIMEOUT_SEC,
        )
    except requests.RequestException as exc:
        raise FinikRequestError("Не удалось связаться с Finik API") from exc

    response_json: Optional[Dict[str, Any]] = None
    if response.content:
        try:
            parsed_json = response.json()
            if isinstance(parsed_json, dict):
                response_json = parsed_json
        except ValueError:
            response_json = None

    payment_url = response.headers.get("Location") or response.headers.get("location")
    finik_payment_id = None
    payment_status = "pending"

    if response_json:
        payment_url = (
            payment_url
            or response_json.get("paymentUrl")
            or response_json.get("payment_url")
        )
        finik_payment_id = (
            response_json.get("paymentId")
            or response_json.get("payment_id")
        )
        response_status = response_json.get("status")
        if response_status:
            payment_status = str(response_status)

    if response.status_code in {301, 302, 303, 307, 308}:
        if not payment_url:
            raise FinikRequestError("Finik вернул redirect без Location")
    elif 200 <= response.status_code < 300:
        if not payment_url:
            raise FinikRequestError("Finik не вернул ссылку на оплату")
    else:
        error_message = _extract_finik_error(response, response_json)
        raise FinikRequestError(f"Finik отклонил запрос: {error_message}")

    return FinikCreatePaymentResult(
        payment_url=payment_url,
        payment_status=payment_status,
        finik_payment_id=str(finik_payment_id) if finik_payment_id else None,
    )
