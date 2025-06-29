import flet as ft
import asyncio
import sys
import os
from app_state import AppState

def resource_path(relative_path):
    """PyInstaller 패키징/로컬 실행 모두에서 리소스 경로 반환"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def create_map_page(page: ft.Page):
    map_width, map_height = 800, 400
    sensor_x, sensor_y = 130, 230

     # 추가: 아무 기능 없는 초록색 원 3개 (위치 조절 가능)
    extra_circles = [
        {"x": 130, "y": 130},
        {"x": 450, "y": 130},
        {"x": 410, "y": 230},
        {"x": 560, "y": 130}
    ]

    extra_circle_controls = [
        ft.Container(
            width=40, height=40, bgcolor="green",
            border_radius=20, left=ec["x"], top=ec["y"],
            border=ft.border.all(2, "black"),
        )
        for ec in extra_circles
    ]
    map_image = ft.Image(
        src=resource_path("source/floor3.png"),
        width=map_width,
        height=map_height,
        fit=ft.ImageFit.CONTAIN
    )

    status_indicator = ft.Container(
        width=40, height=40, bgcolor="green",
        border_radius=20, left=sensor_x, top=sensor_y,
        border=ft.border.all(2, "black")
    )

    status_label = ft.Container(
        content=ft.Text("화재 감지 상태", size=20, weight="bold", color="white", bgcolor="black"),
        padding=10, left=10, top=10
    )

    map_stack = ft.Stack(
        controls=[map_image, status_indicator, status_label] + extra_circle_controls,
        width=map_width, height=map_height
    )
    async def periodic_update():
        while True:
            if getattr(AppState, "alarm_active", False):
                status_indicator.bgcolor = "red"
            else:
                status_indicator.bgcolor = "green"
            map_stack.update()
            await asyncio.sleep(0.5)
            
    buttons = []
    for i in range(1, 6):
        if i == 3:
            btn = ft.ElevatedButton(
                text=str(i),
                bgcolor=ft.colors.RED_300,
                color="white",
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.RED_300,
                    color="white"
                ),
                disabled=True
            )
        else:
            btn = ft.ElevatedButton(
                text=str(i),
                bgcolor=ft.colors.GREY_300,
                color="black"
            )
        buttons.append(btn)

    return (
        ft.Column([
            ft.Text("🏢 건물 안전 상태 지도", size=24, weight="bold"),
            ft.Container(map_stack, alignment=ft.alignment.center),
            ft.Row(buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ]),
        periodic_update
    )
