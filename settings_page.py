import flet as ft
import paho.mqtt.client as mqtt

MQTT_BROKER = "10.40.1.58"
MQTT_PORT = 1883
MQTT_TOPIC = "/modbus/relay44973/out/+"

def create_settings_page(page: ft.Page):
    message_controls = {}  # 토픽별로 메시지를 저장할 딕셔너리

    def toggle_dark_mode(e):
        new_value = e.control.value
        page.theme_mode = ft.ThemeMode.DARK if new_value else ft.ThemeMode.LIGHT
        page.client_storage.set("dark_mode", "true" if new_value else "false")
        page.update()

    message_list = ft.Column(scroll="auto")

    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        # 이미 해당 토픽이 있으면 내용 업데이트
        if topic in message_controls:
            message_controls[topic].value = f"📡 {topic} : {payload}"
        else:
            # 새 토픽이면 새로운 Text 컨트롤 생성 후 딕셔너리에 저장
            message_controls[topic] = ft.Text(f"📡 {topic} : {payload}", size=14)
            message_list.controls.append(message_controls[topic])
        
        page.update()

    def on_connect(client, userdata, flags, rc):
        print("✅ MQTT 설정 페이지 연결됨")
        client.subscribe(MQTT_TOPIC)

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    dark_mode_switch = ft.Switch(
        label="다크 모드",
        value=(page.theme_mode == ft.ThemeMode.DARK),
        on_change=toggle_dark_mode
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("⚙️ 설정 페이지", size=20, weight=ft.FontWeight.BOLD),
            dark_mode_switch,
            ft.Text("🟢 현재 수신 중인 MQTT 토픽 메시지", size=16, weight=ft.FontWeight.BOLD),
            message_list
        ]),
        padding=10
    )
