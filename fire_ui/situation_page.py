import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime

# MQTT 브로커 정보
BROKER = "10.40.1.58"
PORT = 1883
TOPIC = "/modbus/relay44973/out/+"

# 경보 이력 전역 리스트
alarm_history_records = []

# MQTT 클라이언트 전역 객체 생성
mqtt_client = mqtt.Client()

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    topic = msg.topic  

    print(f"MQTT 수신: 토픽={topic}, 메시지={payload}")

    # 특정 토픽에서 "OFF" 신호를 받으면 화재 발생으로 간주
    if topic == "/modbus/relay44973/out/i1" and payload == "OFF":
        fire_alarm_trigger()

def fire_alarm_trigger():
    global page_instance
    if page_instance:
        if page_instance.window.minimized:
            page_instance.window.minimized = False  # 창 복원

        fire_status_text.value = "🔥 화재 감지됨! 🔥"
        fire_status_text.color = "red"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"🚨 [경보] {timestamp} - 화재 감지!"

        if alert_message not in alarm_history_records:
            alarm_history_records.append(alert_message)  # 전역 리스트에 추가
            alarm_history.controls.append(ft.Text(alert_message, size=16, color="red"))

        play_alert_sound()
        page_instance.update()

def play_alert_sound():
    global page_instance
    if page_instance:
        audio = ft.Audio(src="fire_ui\\source\\main_sound.mp3", autoplay=True)
        page_instance.overlay.append(audio)  # 오디오를 overlay에 추가
        page_instance.update()

def connect_mqtt():
    mqtt_client.on_message = on_message  # 메시지 수신 시 실행할 함수
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.subscribe(TOPIC)  # 토픽 구독
    mqtt_client.loop_start()  # 비동기 실행
    print("🔥 MQTT 연결됨! 메시지 대기 중...")

# MQTT 연결 시작 (앱 실행 중 계속 유지됨)
connect_mqtt()

# Flet 페이지 인스턴스 전역 변수
page_instance = None

def create_situation_page(page: ft.Page):
    """ MQTT를 활용한 화재 감지 상황 페이지 UI """
    global page_instance, fire_status_text, alarm_history
    page_instance = page
    
    page.title = "화재 감지 시스템 - 상황 페이지"

    # 현재 감지된 화재 상태 표시
    fire_status_text = ft.Text("현재 감지된 화재 없음", size=20, weight="bold", color="green")

    # 경보 이력을 표시할 ListView
    alarm_history = ft.ListView(expand=True, spacing=10, padding=10)
    
    # 기존 경보 이력 복원 (중복 추가 방지)
    if not alarm_history.controls:
        for record in alarm_history_records:
            alarm_history.controls.append(ft.Text(record, size=16, color="red"))

    # UI 구성
    content = ft.Column(
        controls=[
            ft.Text("📌 실시간 화재 감지 현황", size=24, weight="bold"),
            fire_status_text,
            ft.Text("📜 경보 이력", size=20, weight="bold"),
            alarm_history,
        ],
        spacing=20
    )

    return content