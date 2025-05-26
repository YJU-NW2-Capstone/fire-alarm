import flet as ft
import paho.mqtt.client as mqtt
from app_state import AppState

def create_settings_page(page: ft.Page):
    message_controls = {}
    connection_status = ft.Text("⏳ MQTT 연결 상태 확인 중...", color="orange", size=14)
    mqtt_client = mqtt.Client()

    def toggle_dark_mode(e):
        new_value = e.control.value
        page.theme_mode = ft.ThemeMode.DARK if new_value else ft.ThemeMode.LIGHT
        page.client_storage.set("dark_mode", "true" if new_value else "false")
        page.update()

    broker_input = ft.TextField(label="MQTT 브로커 주소", value=AppState.mqtt_broker)
    apply_button = ft.ElevatedButton(text="적용", on_click=lambda e: apply_new_broker())

    message_list = ft.Column(scroll="auto")

    def apply_new_broker():
        new_broker = broker_input.value.strip()
        if new_broker:
            print(f"🔄 브로커 주소 변경됨: {new_broker}")
            AppState.update_broker(new_broker)
    
            # UI 업데이트
            try:
                mqtt_client.disconnect()
            except:
                pass
    
            try:
                mqtt_client.connect(AppState.mqtt_broker, AppState.mqtt_port, 60)
                mqtt_client.loop_start()
                connection_status.value = f"✅ 연결됨: {AppState.mqtt_broker}"
                connection_status.color = "green"
            except Exception as e:
                connection_status.value = f"❌ 연결 실패: {e}"
                connection_status.color = "red"
            page.update()

    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        if topic in message_controls:
            message_controls[topic].value = f"📡 {topic} : {payload}"
        else:
            message_controls[topic] = ft.Text(f"📡 {topic} : {payload}", size=14)
            message_list.controls.append(message_controls[topic])
        page.update()

    def on_connect(client, userdata, flags, rc):
        print("✅ 설정 페이지 MQTT 연결됨")
        for topic in AppState.mqtt_topics:
            client.subscribe(topic)
            print(f"📡 구독: {topic}")
        connection_status.value = f"✅ 연결됨: {AppState.mqtt_broker}"
        connection_status.color = "green"
        page.update()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # 최초 연결 시도 (실패해도 UI는 동작)
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
            broker_input,
            apply_button,
            connection_status,
            ft.Text("🟢 현재 수신 중인 메시지", size=16, weight=ft.FontWeight.BOLD),
            message_list,
        ]),
        padding=10
    )
