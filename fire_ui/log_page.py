import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta  

log_data = []  #  로그 데이터 저장 리스트
mqtt_client = None  # 전역 MQTT 클라이언트 객체

def create_log_page(page: ft.Page): # 로그 페이지 생성성
    global mqtt_client  # 전역 MQTT 객체 사용

    log_list = ft.ListView(expand=True, spacing=10, auto_scroll=True) # 리스트 생성 

    def add_log(message): 
        timestamp = datetime.now() # 현재 시간을 가져오기기  
        log_entry = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}" # 로그 메세지에 추가가 
        log_data.append((timestamp, log_entry))  # 로그리스트 data에 저장

        # 3일이 지난 로그 삭제
        three_days_ago = datetime.now() - timedelta(days=3)
        log_data[:] = [(t, msg) for t, msg in log_data if t >= three_days_ago]

        # UI 업데이트, 안해주면 화면이 멈춰있음
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
    for _, log in log_data:
        log_list.controls.append(ft.Text(log, size=18))

    page.update()
    
    # MQTT 클라이언트가 이미 실행 중이라면 새로 만들지 않음
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

        def on_message(client, userdata, msg): #메세지 수신시 실행
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            add_log(f"[ {topic} ] {payload}")  

        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        
        try:
            mqtt_client.connect("10.40.1.58", 1883, 60)
            mqtt_client.loop_start() # 계속해서 mqtt메세지 받기
        except Exception as e:
            add_log(f"MQTT 연결 오류: {e}")
    
    return container
