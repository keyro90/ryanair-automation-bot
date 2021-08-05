import os

gc = {
    "token_bot": os.getenv('TELEGRAM_BOT_TOKEN'),
    "chat_ids": os.getenv('CHAT_IDS'),
    "headless": os.getenv('HEADLESS') == 'true',
    "price_point": float(os.getenv('PRICE_POINT')) if os.getenv('PRICE_POINT') else 0,
    "driver_pathname": os.getenv('DRIVER_PATHNAME') or "./geckodriver"
}
