import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime
import os

# MQTT 브로커 정보
BROKER = "10.40.1.58"
PORT = 1883
TOPIC = "/modbus/relay44973/out/+"

# 로그 저장 파일
LOG_FILE = "alarm_history.txt"

# 경보 이력 전역 리스트
alarm_history_records = []
current_audio = None  # 현재 재생 중인 알림음 객체 저장

# MQTT 클라이언트 전역 객체 생성
mqtt_client = mqtt.Client()

def load_logs():
    """파일에서 기존 로그를 불러옴"""
    global alarm_history_records
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            alarm_history_records = [line.strip() for line in f.readlines()]

def save_logs():
    """현재 로그를 파일에 저장"""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for record in alarm_history_records:
            f.write(f"{record}\n")

def on_message(client, userdata, msg):
    """MQTT 메시지 수신 시 실행"""
    payload = msg.payload.decode("utf-8")
    topic = msg.topic  
    print(f"MQTT 수신: 토픽={topic}, 메시지={payload}")

    if topic == "/modbus/relay44973/out/i1" and payload == "OFF":
        fire_alarm_trigger()

def fire_alarm_trigger():
    """화재 감지 시 실행"""
    global page_instance, current_audio
    if page_instance:
        if page_instance.window.minimized:
            page_instance.window.minimized = False  # 창 복원

        fire_status_text.value = "🔥 화재 감지됨! 🔥"
        fire_status_text.color = "red"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"🚨 [경보] {timestamp} - 화재 감지!"

        if alert_message not in alarm_history_records:
            alarm_history_records.append(alert_message)
            alarm_history.controls.append(ft.Text(alert_message, size=16, color="red"))
            save_logs()  # 로그 저장

        # 알림음 재생
        if current_audio is None:
            play_alert_sound()

        page_instance.update()

def play_alert_sound():
    """화재 경보음 재생"""
    global page_instance, current_audio, stop_button
    if page_instance:
        current_audio = ft.Audio(src="fire_ui\\source\\main_sound.mp3", autoplay=True)
        page_instance.overlay.append(current_audio)
        stop_button.visible = True  # "확인" 버튼 보이기
        page_instance.update()

def stop_alert_sound(e):
    """알림음 중지"""
    global page_instance, current_audio, stop_button
    if page_instance and current_audio:
        page_instance.overlay.remove(current_audio)  # 알림음 제거
        current_audio = None
        stop_button.visible = False  # 버튼 숨기기
        page_instance.update()

def connect_mqtt():
    """MQTT 브로커 연결"""
    mqtt_client.on_message = on_message
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.subscribe(TOPIC)
    mqtt_client.loop_start()
    print("🔥 MQTT 연결됨! 메시지 대기 중...")

# MQTT 연결 시작
connect_mqtt()

# Flet 페이지 인스턴스 전역 변수
page_instance = None
stop_button = None  # "확인" 버튼 객체

def create_situation_page(page: ft.Page):
    """화재 감지 상황 페이지 UI"""
    global page_instance, fire_status_text, alarm_history, stop_button
    page_instance = page
    page.title = "화재 감지 시스템 - 상황 페이지"

    # 현재 감지된 화재 상태 표시
    fire_status_text = ft.Text("현재 감지된 화재 없음", size=20, weight="bold", color="green")

    # 경보 이력을 표시할 ListView
    alarm_history = ft.ListView(expand=True, spacing=10, padding=10)

    # 기존 경보 이력 복원
    load_logs()
    alarm_history.controls.clear()
    for record in alarm_history_records:
        alarm_history.controls.append(ft.Text(record, size=16, color="red"))

    # "확인" 버튼 (초기에는 숨김)
    stop_button = ft.ElevatedButton(
        text="확인", 
        on_click=stop_alert_sound,
        visible=False  # 기본적으로 숨겨둠
    )

    # UI 구성
    content = ft.Column(
        controls=[
            ft.Text("📌 실시간 화재 감지 현황", size=24, weight="bold"),
            fire_status_text,
            stop_button,  # "확인" 버튼 추가
            ft.Text("📜 경보 이력", size=20, weight="bold"),
            alarm_history,
        ],
        spacing=20
    )

    return content
