import flet as ft
import datetime
import asyncio
import os
import sys
from app_state import AppState

fire_status = "현재 감지된 화재 없음"
alarm_history = []
current_audio = None
HISTORY_FILE = "alarm_history.txt"

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

DEFAULT_IMAGE = resource_path("source/찐메인.png")
ALARM_IMAGE = resource_path("source/image-removebg-preview.png")

def load_alarm_history():
    global alarm_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            alarm_history = file.read().splitlines()

def save_alarm_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(alarm_history))

def create_main_page(page: ft.Page):
    global fire_status, alarm_history, current_audio

    fire_status_text = ft.Text(size=20, weight="bold")
    alarm_history_list = ft.ListView(expand=True, spacing=10, padding=10)
    fire_image = ft.Image(src=DEFAULT_IMAGE, width=300, height=300)

    def update_ui_by_fire_status():
        if fire_status == "🔥 화재 감지됨! 🔥":
            fire_status_text.value = fire_status
            fire_status_text.color = "red"
            fire_image.src = ALARM_IMAGE
        else:
            fire_status_text.value = "현재 감지된 화재 없음"
            fire_status_text.color = "green"
            fire_image.src = DEFAULT_IMAGE
        fire_image.key = str(datetime.datetime.now().timestamp())  # 강제로 UI 갱신
        page.update()

    def update_alarm_history():
        alarm_history_list.controls.clear()
        for msg in alarm_history:
            alarm_history_list.controls.append(ft.Text(msg, size=16, color="red"))
        page.update()

    def play_alert_sound():
        global current_audio
        current_audio = ft.Audio(src="source/main_sound.mp3", autoplay=True)
        page.overlay.append(current_audio)
        page.update()

    def stop_alert_sound(e=None):
        global current_audio, fire_status
        if current_audio and current_audio in page.overlay:
            page.overlay.remove(current_audio)
            current_audio = None
        fire_status = "현재 감지된 화재 없음"
        update_ui_by_fire_status()

    def fire_alarm_trigger():
        global fire_status, alarm_history
        if page.window.minimized:
            page.window.minimized = False
        play_alert_sound()
        fire_status = "🔥 화재 감지됨! 🔥"
        update_ui_by_fire_status()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alarm_message = f"🚨 [경보] {timestamp} - 화재 감지!"
        alarm_history.append(alarm_message)
        save_alarm_history()
        update_alarm_history()
    
    def on_message(client, userdata, msg):
        try:
            # Ignore retained messages
            if msg.retain:
                print(f"⚠️ Retained 메시지 무시됨: {msg.topic} - {msg.payload.decode('utf-8')}")
                return
            
            payload = msg.payload.decode("utf-8")
            print(f"📩 메시지 수신: {msg.topic} - {payload}")
            if msg.topic == "/modbus/relay44973/out/i1" and payload == "ON":
                fire_alarm_trigger()
            else:
                print("⚠️ 조건 불일치: 화재 트리거 실행되지 않음")
        except Exception as e:
            print(f"❌ 메시지 처리 중 오류 발생: {e}")

    def on_broker_change():
        print("🔄 MQTT 브로커 변경 감지 - 클라이언트 재설정")
        AppState.create_mqtt_client(on_connect=None, on_message=on_message)

        # 토픽 구독
        AppState.mqtt_client.subscribe("/modbus/relay44973/out/i1")
        print("✅ 토픽 구독 완료: /modbus/relay44973/out/i1")

    AppState.add_mqtt_handler(on_broker_change)

    # MQTT 클라이언트 초기화 확인
    if not hasattr(AppState, 'mqtt_client') or AppState.mqtt_client is None:
        print("🔄 MQTT 클라이언트를 초기화합니다.")
        AppState.create_mqtt_client(on_connect=None, on_message=on_message)

        # 토픽 구독
        AppState.mqtt_client.subscribe("/modbus/relay44973/out/i1")
        print("✅ 토픽 구독 완료: /modbus/relay44973/out/i1")

    # 🔄 주기적인 클라이언트 상태 확인
    async def periodic_update():
        while True:
            if not AppState.mqtt_client or not AppState.mqtt_client.is_connected():
                print("⚠️ MQTT 클라이언트 연결 끊김 - 재연결 시도")
                AppState.create_mqtt_client(on_connect=None, on_message=on_message)

                # 토픽 재구독
                AppState.mqtt_client.subscribe("/modbus/relay44973/out/i1")
                print("🔄 재구독 완료: /modbus/relay44973/out/i1")
            update_ui_by_fire_status()
            await asyncio.sleep(1)

    load_alarm_history()
    update_ui_by_fire_status()
    update_alarm_history()

    stop_alarm_button = ft.ElevatedButton("알림음 중지", on_click=stop_alert_sound)

    layout = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("📌 실시간 화재 감지 현황", size=24, weight="bold"),
                    fire_status_text,
                    stop_alarm_button,
                    ft.Text("📜 경보 이력", size=20, weight="bold"),
                    alarm_history_list,
                ],
                spacing=20,
                expand=True
            ),
            fire_image,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    page.run_task(periodic_update)
    return layout

def main(page: ft.Page):
    page.title = "화재 경보 시스템"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_maximized = True

    # 메인 페이지 생성
    main_page_layout = create_main_page(page)

    # UI 추가
    page.add(main_page_layout)
    page.update()

    # 종료 시 MQTT 클라이언트 종료 처리
    def on_close(e):
        if AppState.mqtt_client:
            AppState.mqtt_client.loop_stop()
            AppState.mqtt_client.disconnect()

    page.on_close = on_close

# Flet 앱 실행
if __name__ == "__main__":
    ft.app(target=main)