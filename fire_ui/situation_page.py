import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime
import asyncio
import os

BROKER = "10.40.1.58"
PORT = 1883
TOPIC = "/modbus/relay44973/out/+"
HISTORY_FILE = "alarm_history.txt"  # 🔹 이력 저장 파일

fire_status = "현재 감지된 화재 없음"
alarm_history = []  # 🔥 화재 감지 이력 저장 리스트
mqtt_client = None
current_audio = None

# 📂 이력 파일에서 데이터 불러오기
def load_alarm_history():
    global alarm_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            alarm_history = file.read().splitlines()  # 한 줄씩 읽어서 리스트로 변환

# 💾 현재 이력 데이터를 파일에 저장
def save_alarm_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(alarm_history))  # 리스트를 줄 단위로 저장
    print("💾 화재 이력 저장 완료!")

def create_situation_page(page: ft.Page):
    global mqtt_client, fire_status, alarm_history, current_audio
    page.title = "화재 감지 시스템 - 상황 페이지"

    fire_status_text = ft.Text(fire_status, size=20, weight="bold", color="green")
    alarm_history_list = ft.ListView(expand=True, spacing=10, padding=10)

    # 🔄 UI 업데이트 함수
    def update_alarm_history():
        alarm_history_list.controls.clear()
        for msg in alarm_history:
            alarm_history_list.controls.append(ft.Text(msg, size=16, color="red"))

        if alarm_history_list.page and alarm_history_list.controls:
            alarm_history_list.scroll_to(len(alarm_history_list.controls) - 1)
        page.update()

    # 🔊 알림음 재생
    def play_alert_sound():
        global current_audio
        current_audio = ft.Audio(src="source\\main_sound.mp3", autoplay=True)
        page.overlay.append(current_audio)
        page.update()

    # 🔇 알림음 중지
    def stop_alert_sound(e):
        global current_audio
        if current_audio and current_audio in page.overlay:
            page.overlay.remove(current_audio)
            current_audio = None
            page.update()

    # 🚨 화재 감지 시 UI 업데이트 및 이력 추가
    def fire_alarm_trigger():
        global fire_status, alarm_history
        if page.window.minimized:
            page.window.minimized = False  # 창 복원

        play_alert_sound()

        fire_status = "🔥 화재 감지됨! 🔥"
        fire_status_text.value = fire_status
        fire_status_text.color = "red"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alarm_message = f"🚨 [경보] {timestamp} - 화재 감지!"
        alarm_history.append(alarm_message)  # 리스트에 추가
        save_alarm_history()  # 🔄 이력 파일 저장
        update_alarm_history()  # 🔄 UI 즉시 반영

    # 📩 MQTT 메시지 수신 처리
    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        if topic == "/modbus/relay44973/out/i1" and payload == "ON":
            fire_alarm_trigger()

    # 🛠 MQTT 클라이언트 설정
    if mqtt_client is None:
        mqtt_client = mqtt.Client()
        mqtt_client.on_message = on_message
        try:
            mqtt_client.connect(BROKER, PORT, 60)
            mqtt_client.subscribe(TOPIC)
            mqtt_client.loop_start()
            print("🔥 MQTT 연결됨! 메시지 대기 중...")
        except Exception as e:
            print("❌ MQTT 연결 오류:", e)

    # 🔄 주기적 업데이트 실행
    async def periodic_update():
        while True:
            update_alarm_history()  # 이력을 주기적으로 갱신
            await asyncio.sleep(1)

    # 🆕 앱 실행 시 이전 이력 불러오기
    load_alarm_history()
    update_alarm_history()  # 불러온 이력을 UI에 반영

    # 🔘 알림음 중지 버튼
    stop_alarm_button = ft.ElevatedButton("알림음 중지", on_click=stop_alert_sound)

    # 📜 UI 구성
    content = ft.Column(
        controls=[
            ft.Text("📌 실시간 화재 감지 현황", size=24, weight="bold"),
            fire_status_text,
            ft.Text("📜 경보 이력", size=20, weight="bold"),
            stop_alarm_button,
            alarm_history_list,
        ],
        spacing=20
    )

    # 주기적 업데이트 실행
    page.run_task(periodic_update)

    return content
