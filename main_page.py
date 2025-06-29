import flet as ft
import datetime
import asyncio
import os
import sys
from app_state import AppState
from win10toast import ToastNotifier

fire_status = "현재 감지된 화재 없음"
alarm_history = []
current_audio = None

last_alarm_time = 0
last_alarm_state = None
ALARM_DEBOUNCE_SECONDS = 3
toaster = ToastNotifier()

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
HISTORY_FILE = resource_path("alarm_history.txt")

DEFAULT_IMAGE = resource_path("source/찐메인.png")
ALARM_IMAGE = resource_path("source/image-removebg-preview.png")

def show_fire_notification(room="302호"):
    try:
        toaster.show_toast(
            "화재 발생",
            f"{room}에서 화재가 감지되었습니다!",
            duration=5,
            threaded=True,
            icon_path=None
        )
    except Exception as e:
        print(f"알림 표시 실패: {e}")

def load_alarm_history():
    global alarm_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            alarm_history = file.read().splitlines()

def save_alarm_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(alarm_history))

def create_main_page(page: ft.Page):
    global fire_status, alarm_history, current_audio, last_alarm_time, last_alarm_state

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
        fire_image.key = str(datetime.datetime.now().timestamp())
        page.update()


    def update_alarm_history():
        alarm_history_list.controls.clear()
        for msg in alarm_history:
            alarm_history_list.controls.append(ft.Text(msg, size=16, color="red"))
        page.update()

    load_alarm_history()
    update_alarm_history()

    def play_alert_sound():
        global current_audio
        if current_audio is None:
            current_audio = ft.Audio(src=resource_path("source/main_sound.mp3"), autoplay=True)
            page.overlay.append(current_audio)
            page.update()

    def stop_alert_sound(e=None):
        global current_audio, fire_status
        if current_audio and current_audio in page.overlay:
            page.overlay.remove(current_audio)
            current_audio = None
        fire_status = "현재 감지된 화재 없음"
        AppState.alarm_active = False
        page.window_always_on_top = False
        update_ui_by_fire_status()
        page.update()
        

    def fire_alarm_trigger(message):
        global fire_status, alarm_history, last_alarm_time, last_alarm_state
        now = datetime.datetime.now().timestamp()
        AppState.alarm_active = True
        if last_alarm_state == "ON" and now - last_alarm_time < ALARM_DEBOUNCE_SECONDS:
            print("중복 알람 방지")
            return
        last_alarm_time = now
        last_alarm_state = "ON"

        show_fire_notification(room="302호")

        if page.window.minimized:
            page.window.minimized = False
        play_alert_sound()

        def update_all():
            nonlocal message
            global fire_status
            fire_status = "🔥 화재 감지됨! 🔥"
            update_ui_by_fire_status()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            alarm_message = f"🚨 [경보] {timestamp} - {message}"
            alarm_history.append(alarm_message)
            save_alarm_history()
            load_alarm_history()
            update_alarm_history()
            page.update()

        if hasattr(page, "run_on_main_thread"):
            page.run_on_main_thread(update_all)
        else:
            update_all()

    def on_message(client, userdata, msg):
        try:
            if hasattr(msg, 'retain') and msg.retain:
                print("retain 메시지 무시")
                return

            payload = msg.payload.decode("utf-8")
            print(f"메시지 수신: {msg.topic} - '{payload}'")
            if(AppState.alarm_active==True) : return
            page.update()
            if (msg.topic == "/modbus/relay44973/out/i1" and payload.strip().upper() == "ON"):
                AppState.alarm_active = True
                fire_alarm_trigger("화재 감지!")
            elif (msg.topic == "esp32/302" and "화재 발생" in payload):
                AppState.alarm_active = True
                fire_alarm_trigger("화재 감지! - 302호에서 발생!")
            else:
                AppState.alarm_active = False
            page.update()

        except Exception as e:
            print(f"❌ 메시지 처리 중 오류 발생: {e}")

    if on_message not in AppState.mqtt_handlers:
        AppState.add_mqtt_handler(on_message)

    if AppState.mqtt_client is None:
        AppState.create_mqtt_client()

    async def periodic_update():
        while True:
            if not AppState.mqtt_client or not AppState.mqtt_client.is_connected():
                print("⚠️ MQTT 클라이언트 연결 끊김 - 재연결 시도")
                AppState.create_mqtt_client()
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

    main_page_layout = create_main_page(page)
    page.add(main_page_layout)
    page.update()

    def on_close(e):
        if AppState.mqtt_client:
            AppState.mqtt_client.loop_stop()
            AppState.mqtt_client.disconnect()

    page.on_close = on_close

if __name__ == "__main__":
    ft.app(target=main)
