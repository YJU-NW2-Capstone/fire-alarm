import flet as ft
import datetime
import asyncio # 비동기 작업(실시간 움직임에 필요요)
import paho.mqtt.client as mqtt # mqtt프로토콜 연결및 송수신 담당당
from main_page import create_main_page
from log_page import create_log_page
from situation_page import create_situation_page
from settings_page import create_settings_page

# MQTT 설정
MQTT_BROKER = "10.40.1.58"  # 브로커 주소
MQTT_PORT = 1883  # 브로커 포트
MQTT_TOPIC = "/modbus/relay44973/out/+"  # 구독할 토픽,

def main(page: ft.Page): # 페이지 ui를 구성을 담당 
    page.title = "영진 화재경보 시스템" # 타이틀틀
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_maximized = True # 창을 최대화

    time_text = ft.Text("", size=14, color="white") # 현재 시간을 표시 그러나 초기값은 공백문자열열
    status_bar = ft.Container(ft.Text("시스템 정상 작동 중"), alignment=ft.alignment.center, bgcolor="lightgray", padding=5)
    connection_status = ft.Text("연결 상태: 대기 중", size=14, color="blue")

    # MQTT 클라이언트 객체 생성
    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):# 클라이언트객체, 사용자 데이터, 플래그 정보, 연결결과 코드확인인 
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
        client.loop_start()# 브로커 연결성공시 loop_start로 지속적인 메시지 수신
    except:
        connection_status.value = "연결 상태: 나쁨"
        connection_status.color = "red"

    async def update_time(): # 비동기(실시간간)
        while True:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_text.value = now
            page.update()
            await asyncio.sleep(1)#1초간격으로 실행행

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

    def create_page_with_update(create_func): # 페이지생성 및 업데이트하는 함수
        def wrapper():
            page_content = create_func(page)
            return page_content
        return wrapper

    page_creators = { # 각페이지를 딕셔너리로 관리
        "메인": create_page_with_update(create_main_page),
        "로그": create_page_with_update(create_log_page),
        "상황": create_page_with_update(create_situation_page),
        "설정": create_page_with_update(create_settings_page)
    }

    def change_page(e): #아래 네비에서 선택된 탭에 따라 페이지 변경경
        selected_index = e.control.selected_index
        labels = list(page_creators.keys())
        if 0 <= selected_index < len(labels):
            selected_label = labels[selected_index]
            content_area.content = page_creators[selected_label]()
            page.update()

    nav_rail = ft.NavigationRail( #탭한곳으로 페이지 변경경
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

    page.add(layout) # 기본화면을 메인페이지로 설정정
    
    content_area.content = create_main_page(page)
    
    # 시계 업데이트 실행
    page.run_task(update_time)

    page.window_maximized = True
    page.update()

ft.app(target=main) #flet실행행
