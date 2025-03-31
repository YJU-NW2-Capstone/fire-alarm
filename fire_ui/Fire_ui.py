import flet as ft
import datetime
import asyncio
import paho.mqtt.client as mqtt
from main_page import create_main_page
from log_page import create_log_page
from settings_page import create_settings_page

# MQTT 설정
MQTT_BROKER = "10.40.1.58"
MQTT_PORT = 1883
MQTT_TOPIC = "/modbus/relay44973/out/+"

def main(page: ft.Page):
    page.title = "영진 화재경보 시스템"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_maximized = True

    time_text = ft.Text("", size=14, color="white")
    status_bar = ft.Container(ft.Text("시스템 정상 작동 중"), alignment=ft.alignment.center, bgcolor="lightgray", padding=5)
    connection_status = ft.Text("연결 상태: 대기 중", size=14, color="blue")

    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            connection_status.value = "연결 상태: 좋음"
            connection_status.color = "green"
        else:
            connection_status.value = "연결 상태: 나쁨"
            connection_status.color = "red"
        page.update()

    def on_fire_detected():
        page.window_to_front()
        change_page(2)  # 상황 페이지의 인덱스

    def on_message(client, userdata, msg):
        message = msg.payload.decode("utf-8")
        print(f"MQTT 메시지 수신: {msg.topic} - {message}")
        if "화재 발생" in message:
            on_fire_detected()

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except:
        connection_status.value = "연결 상태: 나쁨"
        connection_status.color = "red"

    async def update_time():
        while True:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_text.value = now
            page.update()
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
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=5,
        padding=10
    )

    def create_page_with_update(create_func):
        def wrapper():
            page_content = create_func(page)
            return page_content
        return wrapper

    page_creators = {
        "메인": create_page_with_update(create_main_page),
        "로그": create_page_with_update(create_log_page),
        "설정": create_page_with_update(create_settings_page)
    }

    nav_destinations = [
        ft.NavigationRailDestination(icon=ft.Icons.HOME, label="메인"),
        ft.NavigationRailDestination(icon=ft.Icons.LIST, label="로그"),
        ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="설정")
    ]

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=nav_destinations,
        on_change=lambda e: change_page(e.control.selected_index)
    )

    def change_page(index):
        labels = list(page_creators.keys())
        if 0 <= index < len(labels):
            selected_label = labels[index]
            content_area.content = page_creators[selected_label]()
            
            # 현재 선택된 페이지의 버튼을 비활성화
            for i, dest in enumerate(nav_destinations):
                dest.disabled = (i == index)
            
            nav_rail.selected_index = index
            nav_rail.destinations = nav_destinations
            page.update()

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
    
    content_area.content = create_main_page(page)
    
    page.run_task(update_time)

    page.window_maximized = True
    page.update()

ft.app(target=main)
