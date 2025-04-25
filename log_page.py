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
mqtt_connected = False  # MQTT 연결 여부 확인용
received_topics = set()  # 수신된 토픽 추적용

# 디바운스 타이머 설정
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
    if not mqtt_connected:
        print("⚠️ MQTT 연결되지 않음, 로그 기록 생략")
        return

    # 모든 토픽이 수신되지 않았으면 기록하지 않음
    if len(received_topics) < len(MQTT_TOPICS):
        print("⚠️ 모든 MQTT 토픽 수신 안 됨, 로그 기록 생략")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (f"[{timestamp}] r1: {mqtt_values['/modbus/relay44973/out/r1']}, "
                 f"r2: {mqtt_values['/modbus/relay44973/out/r2']}, "
                 f"i1: {mqtt_values['/modbus/relay44973/out/i1']}, "
                 f"i2: {mqtt_values['/modbus/relay44973/out/i2']}")

    logger.info(log_entry)

    log_list.controls.append(ft.Text(log_entry, size=14))

# 디바운스 후 로그 업데이트
def on_debounce_complete():
    global global_log_list
    if global_log_list is None:
        return
    update_and_add_log(global_log_list)
    if global_log_list.page is not None:
        global_log_list.page.update()

# MQTT 초기화
def init_mqtt():
    def on_connect(client, userdata, flags, rc):
        global mqtt_connected
        if rc == 0:
            mqtt_connected = True
            print("✅ MQTT 연결 성공")
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
        else:
            mqtt_connected = False
            print("❌ MQTT 연결 실패")

    def on_message(client, userdata, msg):
        global debounce_timer, global_log_list

        if msg.retain:
            print(f"⚠️ Retained 메시지 무시: {msg.topic}")
            return

        if msg.topic in mqtt_values:
            mqtt_values[msg.topic] = msg.payload.decode("utf-8")
            received_topics.add(msg.topic)

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
        print(f"MQTT 연결 오류: {e}")
        if global_log_list is not None:
            global_log_list.controls.append(ft.Text(f"MQTT 연결 오류: {e}", size=14))

# 로그 페이지 생성
def create_log_page(page: ft.Page) -> ft.Container:
    global global_log_list, global_log_initialized

    if global_log_list is None:
        global_log_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

        # 기존 로그 불러오기
        for log in load_logs_from_file():
            global_log_list.controls.append(ft.Text(log, size=14))

        # MQTT 초기화 (한 번만)
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
