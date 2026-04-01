import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'server'))

try:
    from config import settings
    from services.finik import create_payment_link, FinikConfigError, FinikRequestError

    create_payment_link(
        payment_id="test",
        amount=100,
        redirect_url="http://localhost",
        webhook_url="http://localhost",
    )
    print("Success")
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
