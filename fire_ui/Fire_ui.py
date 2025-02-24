import flet as ft
import datetime
import asyncio
import paho.mqtt.client as mqtt
from main_page import create_main_page
from log_page import create_log_page
from situation_page import create_situation_page
from settings_page import create_settings_page

# MQTT 설정
MQTT_BROKER = "172.21.4.168"  # 브로커 주소
MQTT_PORT = 1883  # 브로커 포트
MQTT_TOPIC = "/modbus/relay44973/out/+"  # 구독할 토픽

def main(page: ft.Page):
    page.title = "영진 화재경보 시스템"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_maximized = True

    time_text = ft.Text("", size=14, color="white")
    status_bar = ft.Container(ft.Text("시스템 정상 작동 중"), alignment=ft.alignment.center, bgcolor="lightgray", padding=5)
    connection_status = ft.Text("연결 상태: 대기 중", size=14, color="blue")

    # MQTT 클라이언트 설정
    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            connection_status.value = "연결 상태: 좋음"
            connection_status.color = "green"
        else:
            connection_status.value = "연결 상태: 나쁨"
            connection_status.color = "red"
        page.update()

    def on_message(client, userdata, msg):
        # 메시지 수신 시 처리 로직
        pass

    client.on_connect = on_connect
    client.on_message = on_message

    # MQTT 연결
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        connection_status.value = "연결 상태: 나쁨"
        connection_status.color = "red"
        print("MQTT 연결 오류:", e)

    async def update_time():
        while True:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_text.value = now
            page.update()  # 동기 업데이트 방식 사용
            await asyncio.sleep(1)

    fire_label = ft.Container(
        content=ft.Text("FIRE", size=24, weight=ft.FontWeight.BOLD, color="red"),
        margin=ft.margin.only(left=25)
    )

    time_label = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ACCESS_TIME, color="white", size=16),
            time_text
        ], spacing=5),
        bgcolor="black",
        padding=ft.padding.all(5),
        border_radius=5,
    )

    content_area = ft.Container(
        expand=True,
        border=ft.border.all(1, ft.colors.GREY_400),
        border_radius=5,
        padding=10
    )

    # 만약 페이지 내용에서 동적 업데이트 함수가 필요하다면 update_signal 속성을 추가할 수 있음
    async def global_update():
        while True:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_text.value = now
            if hasattr(content_area.content, 'update_signal'):
                await content_area.content.update_signal()
            page.update()  # 여기서 await page.update_async() 대신 page.update() 사용
            await asyncio.sleep(1)

    def create_page_with_update(create_func):
        def wrapper():
            page_content = create_func(page)
            if hasattr(page_content, 'update_signal'):
                page.run_task(page_content.update_signal)
            return page_content
        return wrapper

    page_creators = {
        "메인": create_page_with_update(create_main_page),
        "로그": create_page_with_update(create_log_page),
        "상황": create_page_with_update(create_situation_page),
        "설정": create_page_with_update(create_settings_page)
    }

    def change_page(e):
        selected_index = e.control.selected_index
        labels = list(page_creators.keys())

        if 0 <= selected_index < len(labels):
            selected_label = labels[selected_index]
            new_content = page_creators[selected_label]()  # 새로운 페이지 생성
            
            # 기존 내용을 교체 후 content_area 업데이트
            content_area.content = new_content
            content_area.update()

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.HOME, label="메인"),
            ft.NavigationRailDestination(icon=ft.Icons.LIST, label="로그"),
            ft.NavigationRailDestination(icon=ft.Icons.ASSESSMENT, label="상황"),
            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="설정")
        ],
        on_change=change_page
    )

    layout = ft.Column([
        ft.Row([
            fire_label,
            time_label,
            connection_status
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([
            nav_rail,
            ft.VerticalDivider(width=1),
            content_area
        ], expand=True),
        status_bar
    ], expand=True)

    page.add(layout)
    
    # 초기 페이지 설정
    content_area.content = create_main_page(page)
    content_area.update()

    # 시간 업데이트 작업 실행 (필요에 따라 global_update 대신 사용)
    page.run_task(update_time)
    # page.run_task(global_update)  # 둘 중 하나만 실행

    page.window_maximized = True
    page.update()

ft.app(target=main)
