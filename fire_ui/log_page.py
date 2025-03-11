import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta  
import os

LOG_FILE = "log_data.txt"  # 로그 저장 파일 경로
log_data = []  # 로그 데이터를 저장할 리스트
mqtt_client = None  # 전역 MQTT 클라이언트 객체

def load_logs():
    """파일에서 로그를 불러옵니다."""
    global log_data
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                timestamp_str, message = line.strip().split("] ", 1)
                timestamp = datetime.strptime(timestamp_str[1:], "%Y-%m-%d %H:%M:%S")
                log_data.append((timestamp, f"[{timestamp_str[1:]}] {message}"))

def save_logs():
    """로그 데이터를 파일에 저장합니다."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for timestamp, log_entry in log_data:
            f.write(f"{log_entry}\n")

def create_log_page(page: ft.Page):
    global mqtt_client 

    log_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)  

    def add_log(message): 
        timestamp = datetime.now()  
        log_entry = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}"  
        log_data.append((timestamp, log_entry))  

        # 3일이 지난 로그 삭제
        three_days_ago = datetime.now() - timedelta(days=3)
        log_data[:] = [(t, msg) for t, msg in log_data if t >= three_days_ago]

        save_logs()  # 로그를 파일에 저장

        log_list.controls.clear()
        for _, log in log_data:
            log_list.controls.append(ft.Text(log, size=18))
        
        page.update()

    container = ft.Container(
        content=ft.Column([
            ft.Text("로그 페이지", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(  
                content=log_list,
                height=400,  
                expand=True,
                border=ft.border.all(1, ft.colors.GREY_400),
                padding=10,
            )
        ]),
        padding=10,
        expand=True
    )
    
    container.add_log = add_log  

    # 기존 로그 불러오기
    load_logs()
    log_list.controls.clear()
    for _, log in log_data:
        log_list.controls.append(ft.Text(log, size=18))

    page.update()
    
    if mqtt_client is None:
        mqtt_client = mqtt.Client()

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
            add_log(f"[ {topic} ] {payload}")  

        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        
        try:
            mqtt_client.connect("10.40.1.58", 1883, 60)
            mqtt_client.loop_start()
        except Exception as e:
            add_log(f"MQTT 연결 오류: {e}")
    
    return container
