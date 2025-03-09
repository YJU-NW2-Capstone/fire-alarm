import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime

# MQTT 브로커 정보
BROKER = "10.40.1.58"
PORT = 1883
TOPIC = "/modbus/relay44973/out/+"

def create_situation_page(page: ft.Page):
    """ MQTT를 활용한 화재 감지 상황 페이지 UI """
    
    page.title = "화재 감지 시스템 - 상황 페이지"

    # 현재 감지된 화재 상태 표시
    fire_status_text = ft.Text("현재 감지된 화재 없음", size=20, weight="bold", color="green")

    # 경보 이력을 표시할 ListView
    alarm_history = ft.ListView(expand=True, spacing=10, padding=10)

    # 🔊 알람 소리 재생 함수
    def play_alert_sound():
        audio = ft.Audio(src="fire_ui\source\main_sound.mp3", autoplay=True)
        page.overlay.append(audio)  # 오디오를 overlay에 추가
        page.update()

    # 🚨 화재 감지 시 UI 업데이트 함수
    def fire_alarm_trigger():
        if page.window.minimized:
            page.window.minimized = False  # 창 복원

        fire_status_text.value = "🔥 화재 감지됨! 🔥"
        fire_status_text.color = "red"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alarm_history.controls.append(ft.Text(f"🚨 [경보] {timestamp} - 화재 감지!", size=16, color="red"))

        play_alert_sound()
        page.update()

    # ✅ MQTT 메시지 수신 시 실행되는 함수
    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic  

        print(f"MQTT 수신: 토픽={topic}, 메시지={payload}")

        # 특정 토픽에서 "OFF" 신호를 받으면 화재 발생으로 간주
        if topic == "/modbus/relay44973/out/i1" and payload == "OFF":
            fire_alarm_trigger()

    # 🔗 MQTT 연결 및 설정
    def connect_mqtt():
        client = mqtt.Client()
        client.on_message = on_message  # 메시지 수신 시 실행할 함수
        client.connect(BROKER, PORT, 60)
        client.subscribe(TOPIC)  # 토픽 구독
        client.loop_start()  # 비동기 실행
        print("🔥 MQTT 연결됨! 메시지 대기 중...")

    # 페이지가 로드될 때 MQTT 연결
    connect_mqtt()

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
