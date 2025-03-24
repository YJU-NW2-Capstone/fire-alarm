import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime
import asyncio

# MQTT 브로커 정보
BROKER = "10.40.1.58"
PORT = 1883
TOPIC = "/modbus/relay44973/out/+"

# 전역 상태 변수
fire_status = "현재 감지된 화재 없음"
alarm_history = []
mqtt_client = None  # MQTT 클라이언트를 전역으로 관리
current_audio = None  # 현재 재생 중인 알림음 Audio 객체 저장

def create_situation_page(page: ft.Page):
    global mqtt_client, fire_status, alarm_history, current_audio
    page.title = "화재 감지 시스템 - 상황 페이지"

    # UI 요소 생성
    fire_status_text = ft.Text(fire_status, size=20, weight="bold", color="green")
    alarm_history_list = ft.ListView(expand=True, spacing=10, padding=10)

    # 알람 이력을 업데이트하는 함수
    def update_alarm_history():
        alarm_history_list.controls.clear()
        for msg in alarm_history:
            alarm_history_list.controls.append(ft.Text(msg, size=16, color="red"))
        # ListView가 페이지에 추가된 이후에만 scroll_to 호출
        if alarm_history_list.page is not None and alarm_history_list.controls:
            alarm_history_list.scroll_to(len(alarm_history_list.controls) - 1)
        page.update()

    # 알림음 재생 함수 (audio 객체를 저장)
    def play_alert_sound():
        global current_audio
        current_audio = ft.Audio(src="source\\main_sound.mp3", autoplay=True)
        page.overlay.append(current_audio)
        page.update()

    # 알림음을 중지하는 함수
    def stop_alert_sound(e):
        global current_audio
        if current_audio and current_audio in page.overlay:
            page.overlay.remove(current_audio)
            current_audio = None
            page.update()

    # 화재 발생 시 즉시 UI 업데이트 및 알람 이력 기록
    def fire_alarm_trigger():
        global fire_status, alarm_history
        if page.window.minimized:
            page.window.minimized = False  # 창 복원

        # 알림음 즉시 재생
        play_alert_sound()

        # 즉시 UI 업데이트 진행
        fire_status = "🔥 화재 감지됨! 🔥"
        fire_status_text.value = fire_status
        fire_status_text.color = "red"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alarm_message = f"🚨 [경보] {timestamp} - 화재 감지!"
        alarm_history.append(alarm_message)
        update_alarm_history()  # 알람 이력 UI 업데이트

    # MQTT 메시지 수신 시 호출되는 콜백 함수
    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        # i1 토픽에서 "OFF" 메시지가 오면 즉시 화재 발생 처리
        if topic == "/modbus/relay44973/out/i1" and payload == "OFF":
            fire_alarm_trigger()

    # MQTT 클라이언트가 이미 생성되지 않은 경우에만 생성
    if mqtt_client is None:
        mqtt_client = mqtt.Client()
        mqtt_client.on_message = on_message
        try:
            mqtt_client.connect(BROKER, PORT, 60)
            mqtt_client.subscribe(TOPIC)
            mqtt_client.loop_start()
            print("🔥 MQTT 연결됨! 메시지 대기 중...")
        except Exception as e:
            print("MQTT 연결 오류:", e)

    # 주기적으로 알람 이력을 갱신하는 비동기 작업
    async def periodic_update():
        while True:
            update_alarm_history()
            await asyncio.sleep(1)  # 1초마다 업데이트

    # "알림음 중지" 버튼 추가
    stop_alarm_button = ft.ElevatedButton("알림음 중지", on_click=stop_alert_sound)

    # 페이지 UI 구성
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

    # 페이지 로드시 주기적 업데이트 작업 실행
    page.run_task(periodic_update)

    return content
