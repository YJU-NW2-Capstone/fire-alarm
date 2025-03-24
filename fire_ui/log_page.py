import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime
import logging
import json
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "mqtt_log.log")

# 로깅 설정 (로그는 메모장 파일(mqtt_log.log)에 기록됩니다)
logger = logging.getLogger("MQTT_Logger")
logger.setLevel(logging.DEBUG)

# FileHandler는 기본적으로 append 모드("a")입니다.
file_handler = logging.FileHandler("mqtt_log.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# MQTT 관련 전역 변수
mqtt_values = {
    "/modbus/relay44973/out/lwt_availability": "N/A",
    "/modbus/relay44973/out/r1": "N/A",
    "/modbus/relay44973/out/r2": "N/A",
    "/modbus/relay44973/out/i1": "N/A",
    "/modbus/relay44973/out/i2": "N/A",
}
mqtt_client = None
is_first_connect = True

def load_logs_from_file():
    """메모장 파일(mqtt_log.log)에 기록된 이전 로그들을 불러옵니다."""
    logs = []
    if os.path.exists("mqtt_log.log"):
        try:
            with open("mqtt_log.log", "r", encoding="utf-8") as f:
                logs = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print("로그 파일을 불러오는 중 오류 발생:", e)
    return logs

def create_log_page(page: ft.Page) -> ft.Container:
    global mqtt_client, is_first_connect

    # 메모장 파일에서 이전 기록을 불러옵니다.
    previous_logs = load_logs_from_file()

    log_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    # 이전 로그들을 ListView에 추가
    for log_entry in previous_logs:
        log_list.controls.append(ft.Text(log_entry, size=18))

    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("로그 페이지", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=log_list,
                    height=400,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_400),  # Colors enum 사용
                    padding=10,
                ),
            ]
        ),
        padding=10,
        expand=True,
    )

    def add_log(message: str):
        """
        새로운 로그 메시지를 생성하여 기록하고, 동시에 메모장 파일과 UI ListView에 기록합니다.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        # 로거에 기록 → 파일에도 기록됩니다.
        logger.info(log_entry)
        # UI에 반영 (현재 페이지에 ListView가 붙어있다면)
        log_list.controls.append(ft.Text(log_entry, size=18))
        if log_list.page is not None:
            log_list.scroll_to(len(log_list.controls) - 1)
        page.update()

    if mqtt_client is None:
        mqtt_client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            global is_first_connect
            # 모든 토픽 구독
            for topic in mqtt_values.keys():
                client.subscribe(topic)
            if is_first_connect:
                add_log("MQTT 연결 성공 및 토픽 구독 완료")
                is_first_connect = False

        def on_message(client, userdata, msg):
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            mqtt_values[topic] = payload

            log_message = json.dumps(
                {key.split("/")[-1]: value for key, value in mqtt_values.items()},
                ensure_ascii=False
            )
            add_log(f"MQTT 메시지 수신: {log_message}")

        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        try:
            mqtt_client.connect("10.40.1.58", 1883, 60)
            mqtt_client.loop_start()
        except Exception as e:
            add_log(f"MQTT 연결 실패: {str(e)}")

    return content

if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "실시간 MQTT 로그 페이지"
        log_page_content = create_log_page(page)
        page.add(log_page_content)
        page.update()

    ft.app(target=main)
