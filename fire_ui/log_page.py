import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta  # 시간 추가

def create_log_page(page: ft.Page):
    log_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)  # 스크롤 가능하게 설정
    log_data = []  # 로그 데이터를 저장할 리스트

    def add_log(message):
        timestamp = datetime.now()  # 현재 시간 저장
        log_entry = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}"  # 시간 + 메시지
        log_data.append((timestamp, log_entry))  # 튜플로 저장 (시간, 메시지)

        # 3일이 지난 로그 삭제
        three_days_ago = datetime.now() - timedelta(days=3)
        log_data[:] = [(t, msg) for t, msg in log_data if t >= three_days_ago]

        # UI 업데이트
        log_list.controls.clear()
        for _, log in log_data:
            log_list.controls.append(ft.Text(log, size=18))
        
        page.update()

    container = ft.Container(
        content=ft.Column([
            ft.Text("로그 페이지", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(  # 고정된 높이를 가진 스크롤 가능한 영역
                content=log_list,
                height=400,  # 원하는 높이로 설정
                expand=True,
                border=ft.border.all(1, ft.colors.GREY_400),
                padding=10,
            )
        ]),
        padding=10,
        expand=True
    )
    
    container.add_log = add_log  # 외부에서 로그 추가 가능하도록 설정
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            add_log("MQTT 연결 성공")
            topics = [
                "/modbus/relay44973/out/lwt_availability",
                "/modbus/relay44973/out/r1",
                "/modbus/relay44973/out/r2",
                "/modbus/relay44973/out/i1",
                "/modbus/relay44973/out/i2",
                "/modbus/relay44973/out/ip",
                "/modbus/relay44973/out/sn",
                "/modbus/relay44973/out/hw_version",
                "/modbus/relay44973/out/sw_version",
            ]
            for topic in topics:
                client.subscribe(topic)
        else:
            add_log(f"MQTT 연결 실패: 코드 {rc}")
    
    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        add_log(f"[ {topic} ] {payload}")  # 메시지에도 시간 포함됨
    
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect("10.40.1.58", 1883, 60)
        mqtt_client.loop_start()
    except Exception as e:
        add_log(f"MQTT 연결 오류: {e}")
    
    return container
