import flet as ft
import datetime
import asyncio

def main(page: ft.Page):
    page.title = "영진 화재경보 시스템"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 800
    page.window_height = 680
    
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
    
    time_text = ft.Text("", size=14, color="white")
    time_label = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.ACCESS_TIME, color="white", size=16),
            time_text
        ], spacing=5),
        bgcolor="black",
        padding=ft.padding.all(5),
        border_radius=5,
    )
    
    status_bar = ft.Container(ft.Text("시스템 정상 작동 중"), alignment=ft.alignment.center, bgcolor="lightgray", padding=5)
    
    content_area = ft.Container(
        content=ft.Text("메인 화면"),
        expand=True,
        border=ft.border.all(1, ft.colors.GREY_400),
        border_radius=5,
        padding=10
    )
    
    def change_page(e):
        content_area.content = ft.Text(f"{e.control.text} 화면")
        page.update()
    
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.HOME, label="메인"),
            ft.NavigationRailDestination(icon=ft.icons.LIST, label="로그"),
            ft.NavigationRailDestination(icon=ft.icons.ASSESSMENT, label="상황"),
            ft.NavigationRailDestination(icon=ft.icons.SETTINGS, label="설정"),
        ],
        on_change=change_page
    )
    
    page.run_task(update_time)
    
    page.add(
        ft.Column([
            ft.Row([
                fire_label,
                time_label
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                nav_rail,
                ft.VerticalDivider(width=1),
                content_area
            ], expand=True),
            status_bar
        ], expand=True)
    )

ft.app(target=main)
