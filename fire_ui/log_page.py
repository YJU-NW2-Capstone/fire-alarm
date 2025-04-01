import flet as ft
import os
import datetime
import logging
import logging.handlers
import threading
import paho.mqtt.client as mqtt

LOG_FILE = "mqtt_log.log"
logger = logging.getLogger("MQTT_Logger")
logger.setLevel(logging.DEBUG)
file_handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

MQTT_BROKER = "10.40.1.58"
MQTT_PORT = 1883
MQTT_TOPICS = [
    "/modbus/relay44973/out/r1",
    "/modbus/relay44973/out/r2",
    "/modbus/relay44973/out/i1",
    "/modbus/relay44973/out/i2"
]
mqtt_client = mqtt.Client()
mqtt_values = {topic: "N/A" for topic in MQTT_TOPICS}

global_log_list = None
global_log_initialized = False

# 디바운스 타이머 설정 (예: 0.5초)
DEBOUNCE_INTERVAL = 0.5
debounce_timer = None


def load_logs_from_file():
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = [line.strip() for line in f if line.strip() and "info" not in line.lower()]
        except Exception as e:
            print("로그 파일 로딩 오류:", e)
    return logs


def update_and_add_log(log_list):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (f"[{timestamp}] r1: {mqtt_values['/modbus/relay44973/out/r1']}, "
                 f"r2: {mqtt_values['/modbus/relay44973/out/r2']}, "
                 f"i1: {mqtt_values['/modbus/relay44973/out/i1']}, "
                 f"i2: {mqtt_values['/modbus/relay44973/out/i2']}")
    
    # 로그 파일에 기록
    logger.info(log_entry)
    
    # 앱 UI 업데이트
    log_list.controls.append(ft.Text(log_entry, size=14))


def on_debounce_complete():
    # 모든 토픽의 값이 갱신되었는지 확인 후 로그 기록
    if all(mqtt_values[topic] != "N/A" for topic in MQTT_TOPICS):
        update_and_add_log(global_log_list)
        # 페이지 업데이트 (global_log_list가 포함된 페이지가 있음을 전제)
        global_log_list.page.update()


def init_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
    def on_message(client, userdata, msg):
        global debounce_timer
        if msg.topic in mqtt_values:
            mqtt_values[msg.topic] = msg.payload.decode("utf-8")
        
        # 디바운스 방식 적용: 타이머가 있으면 취소하고 새로 시작
        if debounce_timer is not None:
            debounce_timer.cancel()
        debounce_timer = threading.Timer(DEBOUNCE_INTERVAL, on_debounce_complete)
        debounce_timer.start()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        if global_log_list is not None:
            global_log_list.controls.append(ft.Text(f"MQTT 연결 오류: {e}", size=14))


def create_log_page(page: ft.Page) -> ft.Container:
    global global_log_list, global_log_initialized
    if global_log_list is None:
        global_log_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        for log in load_logs_from_file():
            global_log_list.controls.append(ft.Text(log, size=14))
        if not global_log_initialized:
            init_mqtt()
            global_log_initialized = True
    return ft.Container(
        content=ft.Column([
            ft.Text("로그 페이지", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=global_log_list,
                height=400,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_400),
                padding=10,
            ),
        ]),
        padding=10,
        expand=True,
    )
