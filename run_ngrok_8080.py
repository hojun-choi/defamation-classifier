# run_ngrok_8080.py
import os
from pyngrok import ngrok
from dotenv import load_dotenv

# ==========================================
# 1. .env2 로드
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env2")
load_dotenv(env_path)

NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")
NGROK_HOSTNAME = os.getenv("NGROK_HOSTNAME")  # 선택 사항
APP_PORT = int(os.getenv("APP_PORT", "8080"))  # 기본 8080

if not NGROK_AUTHTOKEN:
    raise RuntimeError("NGROK_AUTHTOKEN 값이 .env 에 없습니다.")

# ==========================================
# 2. ngrok 설정 (토큰 세팅 + 기존 터널 종료)
# ==========================================
print("🔧 ngrok 설정 중...")

ngrok.set_auth_token(NGROK_AUTHTOKEN)
# 혹시 이전에 떠 있던 ngrok 프로세스가 있으면 정리
ngrok.kill()

# ==========================================
# 3. 터널 열기
#    - NGROK_HOSTNAME 이 있으면 그 호스트네임으로
#    - 없으면 랜덤 도메인으로
# ==========================================
connect_kwargs = {}

if NGROK_HOSTNAME:
    # ngrok에 예약된 hostname이 있다면 사용
    # (hostname 옵션은 ngrok/pyngrok에서 커스텀 도메인에 사용됨)
    connect_kwargs["options"] = {"hostname": NGROK_HOSTNAME}
    print(f"🌐 예약 호스트네임로 터널 시도: {NGROK_HOSTNAME}")
else:
    print("🌐 호스트네임 미설정 → 랜덤 ngrok 주소로 터널 생성")

tunnel = ngrok.connect(APP_PORT, "http", **connect_kwargs)
public_url = tunnel.public_url

print("\n=========================================")
print(f"🚀 ngrok 터널 오픈 완료!")
print(f"   ▶ 로컬 서버: http://localhost:{APP_PORT}")
print(f"   ▶ 외부 접속: {public_url}")
print("=========================================\n")

print("⚠️ 이 터미널을 닫거나, 아래에서 엔터를 누르면 ngrok 터널이 종료됩니다.")
input("종료하려면 엔터 키를 누르세요...")

# 스크립트 종료 시 자동으로 터널도 정리됨
print("🛑 ngrok 터널 종료")
