import hashlib
import time

SECRET_KEY = "[r,7?~XPYRZ>~t:weYk}=OY=lY+%q?GL"

def generate_token(time_previous = None) -> str:
    """สร้าง Access Token ด้วย timestamp + client_id + secret key"""
    timestamp = int(time_previous) if time_previous else int(time.time() // 2)
    raw_token = f"{timestamp}{SECRET_KEY}"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return token_hash



def verify_token(token: str) -> bool:
    """ตรวจสอบว่า Token ถูกต้องหรือไม่ (รองรับการคลาดเคลื่อน 2 วินาที)"""
    current_token = generate_token()
    previous_token = generate_token(int(time.time() // 2) - 1)
    return token in (current_token, previous_token)
