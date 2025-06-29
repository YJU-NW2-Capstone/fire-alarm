import flet as ft
import paho.mqtt.client as mqtt
from app_state import AppState

def create_settings_page(page: ft.Page):
    connection_status = ft.Text("⏳ MQTT 연결 상태 확인 중...", color="orange", size=14)
    mqtt_client = mqtt.Client()
    message_list = ft.ListView(
        expand=True,
        spacing=5,
        auto_scroll=True,
        height=300
    )
    # 토픽별 최신값 저장
    latest_messages = {}

    def toggle_dark_mode(e):
        new_value = e.control.value
        page.theme_mode = ft.ThemeMode.DARK if new_value else ft.ThemeMode.LIGHT
        page.client_storage.set("dark_mode", "true" if new_value else "false")
        page.update()

    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        excluded_topics = [
            "/modbus/relay44973/out/r1",
            "/modbus/relay44973/out/r2",
            "/modbus/relay44973/out/i1",
            "/modbus/relay44973/out/i2",
            "esp32/302"
        ]
        if topic in excluded_topics:
            return

        latest_messages[topic] = payload

        def update_ui():
            if getattr(message_list, "page", None) is not None:
                message_list.controls.clear()
                for t, p in latest_messages.items():
                    message_list.controls.append(ft.Text(f"📡 {t} : {p}", size=14))
                message_list.update()

        if hasattr(page, "run_on_main_thread"):
            page.run_on_main_thread(update_ui)
        elif hasattr(page, "invoke"):
            page.invoke(update_ui)
        else:
            update_ui()

    def on_connect(client, userdata, flags, rc):
        print("✅ 설정 페이지 MQTT 연결됨")
        client.subscribe("#")
        print("📡 모든 토픽(#) 구독")
        connection_status.value = f"✅ 연결됨: {AppState.mqtt_broker}"
        connection_status.color = "green"
        page.update()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    try:
        mqtt_client.connect(AppState.mqtt_broker, AppState.mqtt_port, 60)
        mqtt_client.loop_start()
    except Exception as e:
        connection_status.value = f"❌ 연결 실패: {e}"
        connection_status.color = "red"

    dark_mode_switch = ft.Switch(
        label="다크 모드",
        value=(page.theme_mode == ft.ThemeMode.DARK),
        on_change=toggle_dark_mode
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("⚙️ 설정 페이지", size=20, weight=ft.FontWeight.BOLD),
            dark_mode_switch,
            ft.Text("🔧 MQTT 브로커 설정", size=16),
            connection_status,
            ft.Text("🟢 현재 수신 중인 모든 메시지", size=16, weight=ft.FontWeight.BOLD),
            message_list,
        ], spacing=12),
        padding=20
    )
