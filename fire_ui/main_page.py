import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime
import asyncio
import os

BROKER = "10.40.1.58"
PORT = 1883
TOPIC = "/modbus/relay44973/out/+"
HISTORY_FILE = "alarm_history.txt"

fire_status = "현재 감지된 화재 없음"
alarm_history = []
mqtt_client = None
current_audio = None

DEFAULT_IMAGE = "source\찐메인.png"  # 🔹 기본 이미지 (안전 상태)
ALARM_IMAGE = "source\image-removebg-preview.png"  # 🔥 화재 발생 이미지

def load_alarm_history():
    global alarm_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            alarm_history = file.read().splitlines()

def save_alarm_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(alarm_history))
    print("💾 화재 이력 저장 완료!")

def create_main_page(page: ft.Page):
    global mqtt_client, fire_status, alarm_history, current_audio
    page.title = "화재 감지 시스템 - 메인 페이지"

    fire_status_text = ft.Text(fire_status, size=20, weight="bold", color="green")
    alarm_history_list = ft.ListView(expand=True, spacing=10, padding=10)

    # 🔹 화재 상태 이미지
    fire_image = ft.Image(src=DEFAULT_IMAGE, width=300, height=300)

    def update_alarm_history():
        alarm_history_list.controls.clear()
        for msg in alarm_history:
            alarm_history_list.controls.append(ft.Text(msg, size=16, color="red"))

        if alarm_history_list.page and alarm_history_list.controls:
            alarm_history_list.scroll_to(len(alarm_history_list.controls) - 1)
        page.update()

    def play_alert_sound():
        global current_audio
        current_audio = ft.Audio(src="source/main_sound.mp3", autoplay=True)
        page.overlay.append(current_audio)
        page.update()

    def stop_alert_sound(e):
        global current_audio
        if current_audio and current_audio in page.overlay:
            page.overlay.remove(current_audio)
            current_audio = None
        
        # 🔹 화재 종료 시 기본 이미지 복구
        fire_status_text.value = "현재 감지된 화재 없음"
        fire_status_text.color = "green"
        fire_image.src = DEFAULT_IMAGE
        page.update()

    def fire_alarm_trigger():
        global fire_status, alarm_history
        if page.window.minimized:
            page.window.minimized = False

        play_alert_sound()

        fire_status = "🔥 화재 감지됨! 🔥"
        fire_status_text.value = fire_status
        fire_status_text.color = "red"
        fire_image.src = ALARM_IMAGE  # 🔥 화재 발생 이미지로 변경
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alarm_message = f"🚨 [경보] {timestamp} - 화재 감지!"
        alarm_history.append(alarm_message)
        save_alarm_history()
        update_alarm_history()

    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        if topic == "/modbus/relay44973/out/i1" and payload == "ON":
            fire_alarm_trigger()

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

    async def periodic_update():
        while True:
            update_alarm_history()
            await asyncio.sleep(1)

    load_alarm_history()
    update_alarm_history()

    stop_alarm_button = ft.ElevatedButton("알림음 중지", on_click=stop_alert_sound)

    # 🔹 레이아웃을 가로로 정렬
    content = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("📌 실시간 화재 감지 현황", size=24, weight="bold"),
                    fire_status_text,
                    ft.Text("📜 경보 이력", size=20, weight="bold"),
                    stop_alarm_button,
                    alarm_history_list,
                ],
                spacing=20,
                expand=True
            ),
            fire_image  # 🔥 오른쪽에 화재 상태 이미지 추가
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    page.run_task(periodic_update)

    return content
