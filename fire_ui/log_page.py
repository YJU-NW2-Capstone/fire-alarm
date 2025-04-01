import flet as ft
import os
import datetime
import logging
import logging.handlers
import threading
import paho.mqtt.client as mqtt

# 로그 파일 설정
LOG_FILE = "mqtt_log.log"
logger = logging.getLogger("MQTT_Logger")
logger.setLevel(logging.DEBUG)
file_handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# MQTT 설정
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

# 글로벌 변수
global_log_list = None
global_log_initialized = False

# 디바운스 타이머 설정 (예: 0.5초)
DEBOUNCE_INTERVAL = 0.5
debounce_timer = None


# 로그 파일에서 기존 로그 불러오기
def load_logs_from_file():
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = [line.strip() for line in f if line.strip() and "info" not in line.lower()]
        except Exception as e:
            print("로그 파일 로딩 오류:", e)
    return logs


# 로그를 업데이트하고 UI에 추가
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


# 디바운스 후 로그 업데이트 (MQTT 메시지가 여러 개 연속으로 올 때 중복 방지)
def on_debounce_complete():
    global global_log_list
    if global_log_list is None:
        return  # log_list가 초기화되지 않았으면 실행 안 함

    # 모든 토픽 값이 갱신되었는지 확인
    if all(mqtt_values[topic] != "N/A" for topic in MQTT_TOPICS):
        update_and_add_log(global_log_list)

        # 페이지가 있는 경우만 업데이트 실행
        if global_log_list.page is not None:
            global_log_list.page.update()


# MQTT 초기화
def init_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            for topic in MQTT_TOPICS:
                client.subscribe(topic)

    def on_message(client, userdata, msg):
        global debounce_timer, global_log_list
        if msg.topic in mqtt_values:
            mqtt_values[msg.topic] = msg.payload.decode("utf-8")

        # 디바운스 방식 적용: 기존 타이머가 있으면 취소하고 새로 시작
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


# 로그 페이지 생성
def create_log_page(page: ft.Page) -> ft.Container:
    global global_log_list, global_log_initialized

    # global_log_list가 없으면 새로 생성
    if global_log_list is None:
        global_log_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

        # 기존 로그 불러오기
        for log in load_logs_from_file():
            global_log_list.controls.append(ft.Text(log, size=14))

        # MQTT 한 번만 초기화
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
