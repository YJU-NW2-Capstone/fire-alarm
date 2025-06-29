import flet as ft
import datetime
import asyncio
import paho.mqtt.client as mqtt
from main_page import create_main_page, fire_status 
from map_page import create_map_page
from log_page import create_log_page
from settings_page import create_settings_page
import sys
import os
from app_state import AppState
from plyer import notification

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def main(page: ft.Page):
    page.title = "영진 화재경보 시스템"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_maximized = True
    icon_path = resource_path("source/icon.ico")
    page.window_icon = icon_path

    # 온도/습도 표시 컨트롤
    time_text = ft.Text("", size=14, color="white")
    connection_status = ft.Text("MQTT 연결 상태: 대기 중", size=14, color="blue")
    temperature_text = ft.Text(value="온도: -- °C", size=16, color="blue")
    humidity_text = ft.Text(value="습도: -- %", size=16, color="blue")

    client = mqtt.Client()
    last_message_time = datetime.datetime.now()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            connection_status.value = "MQTT 연결 상태: 좋음"
            connection_status.color = "green"
        else:
            connection_status.value = "MQTT 연결 상태: 나쁨"
            connection_status.color = "red"
        page.update()

    def on_fire_detected():
        global fire_status
        fire_status = "🔥 화재 감지됨! 🔥"
        notification.notify(
            title='화재 발생',
            message='302호에서 화재가 감지되었습니다!',
            timeout=5
        )
        page.window_maximized = True
        page.window_always_on_top = True
        page.update()

    def on_message(client, userdata, msg):
        nonlocal last_message_time
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        # 온도/습도 실시간 갱신
        if topic == "esp32/302":
            try:
                parts = payload.split(",")
                temp_part = parts[0].strip()
                hum_part = parts[1].strip()
                temperature_text.value = temp_part
                humidity_text.value = hum_part
                page.update()
            except Exception as e:
                print(f"온습도 파싱 오류: {e}")
        if "화재 발생" in payload:
            on_fire_detected()
        last_message_time = datetime.datetime.now()

    client.on_connect = on_connect
    client.on_message = on_message

    def connect_mqtt():
        try:
            client.connect(AppState.mqtt_broker, AppState.mqtt_port, 60)
            client.loop_start()
            for topic in AppState.mqtt_topics:
                client.subscribe(topic)
        except Exception:
            connection_status.value = "MQTT 연결 상태: 오류"
            connection_status.color = "red"
            page.update()

    connect_mqtt()

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
            return create_func(page)
        return wrapper

    page_creators = {
        "메인": create_page_with_update(create_main_page),
        "지도": create_page_with_update(create_map_page),
        "로그": create_page_with_update(create_log_page),
        "설정": create_page_with_update(create_settings_page)
    }

    nav_destinations = [
        ft.NavigationRailDestination(icon=ft.Icons.HOME, label="메인"),
        ft.NavigationRailDestination(icon=ft.Icons.MAP, label="지도"),
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
            if selected_label == "지도":
                map_content, periodic_update = create_map_page(page)
                content_area.content = map_content
                page.update()
                page.run_task(periodic_update)
            else:
                content_area.content = page_creators[selected_label]()
                page.update()

    layout = ft.Column([
        ft.Row([
            fire_label,
            time_label,
            ft.Container(
                ft.Row([temperature_text, humidity_text], spacing=10),
                alignment=ft.alignment.center_right,
                margin=ft.margin.only(left=30, right=10)
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([
            nav_rail,
            ft.VerticalDivider(width=1),
            content_area
        ], expand=True),
        ft.Container(
            connection_status,
            alignment=ft.alignment.center,
            bgcolor="lightgray",
            padding=5
        )
    ], expand=True)

    page.add(layout)
    content_area.content = create_main_page(page)

    page.run_task(update_time)
    page.window_maximized = True
    page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.FLET_APP)
