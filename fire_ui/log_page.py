import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import json
import asyncio

# 전역 변수들
log_data = []           # (timestamp, log_entry) 튜플 목록
mqtt_client = None      # 전역 MQTT 클라이언트 객체

mqtt_values = {
    "/modbus/relay44973/out/lwt_availability": "N/A",
    "/modbus/relay44973/out/r1": "N/A",
    "/modbus/relay44973/out/r2": "N/A",
    "/modbus/relay44973/out/i1": "N/A",
    "/modbus/relay44973/out/i2": "N/A",
    "/modbus/relay44973/out/ip": "N/A",
    "/modbus/relay44973/out/sn": "N/A",
    "/modbus/relay44973/out/hw_version": "N/A",
    "/modbus/relay44973/out/sw_version": "N/A",
}  # 최신 상태 저장

# 전역 버퍼: 여러 메시지가 오더라도 마지막 상태만 기록하기 위한 버퍼
log_buffer = None

def create_log_page(page: ft.Page) -> ft.Container:
    global mqtt_client, log_data, log_buffer

    # UI: 로그를 보여줄 ListView 컨트롤 생성
    log_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    
    # 전체 UI 콘텐츠 구성 (제목과 로그 영역)
    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("로그 페이지", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=log_list,
                    height=400,
                    expand=True,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    padding=10,
                ),
            ]
        ),
        padding=10,
        expand=True,
    )

    def add_log(message: str):
        """
        전달받은 문자열(message)을 사용해 새 로그 항목을 생성 및 추가합니다.
        """
        timestamp = datetime.now()
        log_entry = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        log_data.append((timestamp, log_entry))
        
        # 용량 관리: 3일 이상 지난 로그 삭제
        cutoff = datetime.now() - timedelta(days=3)
        log_data[:] = [(t, entry) for t, entry in log_data if t >= cutoff]
        
        # UI에 새 로그 항목 추가
        log_list.controls.append(ft.Text(log_entry, size=18))
        log_list.scroll_to(len(log_list.controls) - 1)
        page.update()

    async def flush_log_buffer():
        """
        1초마다 전역 버퍼(log_buffer)에 값이 있으면 add_log()를 호출하여 로그를 추가한 후 버퍼를 비웁니다.
        flush_log_buffer를 try/except로 감싸, ListView 컨트롤이 더 이상 페이지에 없을 경우 예외를 잡고 종료합니다.
        """
        global log_buffer
        while True:
            if log_buffer is not None:
                try:
                    add_log(log_buffer)
                    log_buffer = None
                except AssertionError:
                    # ListView가 더 이상 페이지에 추가되지 않은 경우 (페이지 전환 등)
                    break
            await asyncio.sleep(1)

    # 수정된 부분: flush_log_buffer 코루틴 함수를 직접 전달합니다.
    page.run_task(flush_log_buffer)

    # MQTT 클라이언트 설정 및 연결
    if mqtt_client is None:
        mqtt_client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            # 연결 상태 메시지는 기록하지 않고 모든 토픽 구독만 수행합니다.
            for topic in mqtt_values.keys():
                client.subscribe(topic)
            page.update()

        def on_message(client, userdata, msg):
            global log_buffer
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            mqtt_values[topic] = payload  # 최신 값 갱신
            # 최신 상태를 JSON 문자열로 변환하여 버퍼에 저장 (이전 메시지는 덮어쓰기됨)
            log_message = json.dumps(
                {key.split("/")[-1]: value for key, value in mqtt_values.items()},
                ensure_ascii=False
            )
            log_buffer = log_message

        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        try:
            mqtt_client.connect("10.40.1.58", 1883, 60)
            mqtt_client.loop_start()
        except Exception as e:
            # 연결 오류가 있으면 무시 (또는 별도 처리 가능)
            pass
        page.update()

    # 기존 로그 기록이 있다면 UI ListView에 반영
    for timestamp, log in log_data:
        entry = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log}"
        log_list.controls.append(ft.Text(entry, size=18))
    page.update()

    return content

# -------------------------------
# 사용 예시: 메인 앱
if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "실시간 로그 페이지 (업데이트 개선됨)"
        log_page_content = create_log_page(page)
        page.add(log_page_content)
        page.update()

    ft.app(target=main)
