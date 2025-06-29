import flet as ft
import os
import datetime
import threading
import time
import paho.mqtt.client as mqtt
from app_state import AppState

LOG_FILE = "mqtt_log.log"
DEBOUNCE_INTERVAL = 0.5  # r/i값 한 줄로 묶기용
debounce_timer = None
# r/i 토픽
ri_topics = [
    "/modbus/relay44973/out/r1",
    "/modbus/relay44973/out/r2",
    "/modbus/relay44973/out/i1",
    "/modbus/relay44973/out/i2"
]
# 302 토픽
topic_302 = "esp32/302"

mqtt_values = {topic: "N/A" for topic in ri_topics}
last_302_log_time = 0
LOG_302_INTERVAL = 45  # 45초

def load_logs_from_file():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = [line.strip() for line in f if line.strip()]
    return logs

def create_log_page(page: ft.Page):
    log_list = ft.ListView(
        controls=[ft.Text(log, size=14) for log in load_logs_from_file()],
        expand=True,
        spacing=10,
        auto_scroll=True
    )

    reconnect_attempts = 0
    mqtt_client = None
    received_ri_topics = set()

    def add_ri_log_entry():
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = f"[{timestamp}] " + " ".join(
            [f"{topic.split('/')[-1]}: {mqtt_values.get(topic, 'N/A')}" for topic in ri_topics]
        )
        def update_ui():
            log_list.controls.append(ft.Text(log, size=14))
            # update() 호출 전 페이지에 추가됐는지 확인
            if getattr(log_list, 'page', None) is not None:
                log_list.update()
            else:
                print('ListView not added to page yet, skipping update')
        # 반드시 메인스레드에서 실행
        if hasattr(page, "run_on_main_thread"):
            page.run_on_main_thread(update_ui)
        else:
            update_ui()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log + "\n")

    def add_302_log_entry(payload):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = f"[{timestamp}] 302: {payload}"
        def update_ui():
            log_list.controls.append(ft.Text(log, size=14))
            if getattr(log_list, 'page', None) is not None:
                log_list.update()
            else:
                print('ListView not added to page yet, skipping update')
        if hasattr(page, "run_on_main_thread"):
            page.run_on_main_thread(update_ui)
        else:
            update_ui()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log + "\n")

    def on_connect(client, userdata, flags, rc):
        nonlocal reconnect_attempts
        if rc == 0:
            reconnect_attempts = 0
            for topic in ri_topics + [topic_302]:
                print(f"구독 시도: {topic}")
                client.subscribe(topic)
            print("MQTT 연결 성공 및 토픽 구독 완료")
        else:
            print("MQTT 연결 실패")

    def on_message(client, userdata, msg):
        global last_302_log_time, debounce_timer
        # retain 메시지는 무시 (실시간 메시지만 처리)
        if getattr(msg, 'retain', False):
            return
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        print(f"on_message 호출됨: {topic} - {payload}")

        # 302는 45초에 한 번만 기록
        if topic == topic_302:
            now = time.time()
            if now - last_302_log_time >= LOG_302_INTERVAL:
                add_302_log_entry(payload)
                last_302_log_time = now
            else:
                print(f"302 로그 생략: {payload}")
            return

        if topic in ri_topics:
            mqtt_values[topic] = payload
            received_ri_topics.add(topic)
            # 조건 없이 항상 기록 (네 토픽이 모두 안 들어와도)
            if debounce_timer is not None:
                debounce_timer.cancel()
            debounce_timer = threading.Timer(DEBOUNCE_INTERVAL, add_ri_log_entry)
            debounce_timer.start()

    def on_disconnect(client, userdata, rc):
        print("MQTT 연결 끊김, 재연결 시도")
        # 재연결 로직 필요시 추가

    def init_mqtt():
        nonlocal mqtt_client
        if mqtt_client is not None:
            try:
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            except Exception:
                pass
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        try:
            print(f"MQTT 브로커 연결 시도: {AppState.mqtt_broker}:{AppState.mqtt_port}")
            mqtt_client.connect(AppState.mqtt_broker, AppState.mqtt_port, 60)
            mqtt_client.loop_start()
        except Exception as e:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log = f"[{timestamp}] MQTT 연결 실패: {e}"
            def update_ui():
                log_list.controls.append(ft.Text(log, size=14))
                if getattr(log_list, 'page', None) is not None:
                    log_list.update()
            if hasattr(page, "run_on_main_thread"):
                page.run_on_main_thread(update_ui)
            else:
                update_ui()
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log + "\n")

    init_mqtt()

    return ft.Container(
        content=ft.Column([
            ft.Text("로그 페이지", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=log_list,
                height=400,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_400),
                padding=10,
            ),
        ]),
        padding=10,
        expand=True,
    )
