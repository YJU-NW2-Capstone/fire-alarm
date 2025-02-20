import flet as ft
import datetime
import asyncio

def main(page: ft.Page):
    page.title = "영진 화재경보 시스템"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 800
    page.window_height = 680
    
    # 현재 시간 표시 함수
    async def update_time():
        while True:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_label.value = now
            page.update()
            await asyncio.sleep(1)  # 1초 대기
    
    # 페이지 컨텐츠
    time_label = ft.Text("", size=14)
    fire_label = ft.Text("FIRE", size=24, weight=ft.FontWeight.BOLD, color="red")
    
    # 추가된 UI 요소
    status_bar = ft.Container(ft.Text("시스템 정상 작동 중"), alignment=ft.alignment.center, bgcolor="lightgray", padding=5)
    
    # 페이지들
    pages = [
        ft.Container(ft.Text("메인 화면"), alignment=ft.alignment.center, visible=True),
        ft.Container(ft.Text("로그 기록"), alignment=ft.alignment.center, visible=False),
        ft.Container(ft.Text("설정 화면"), alignment=ft.alignment.center, visible=False)
    ]
    
    # 페이지 전환 함수
    def change_page(index):
        for i, page_content in enumerate(pages):
            page_content.visible = (i == index)
        page.update()
    
    # 버튼들
    buttons = [
        ft.ElevatedButton("메인", on_click=lambda _: change_page(0)),
        ft.ElevatedButton("로그", on_click=lambda _: change_page(1)),
        ft.ElevatedButton("설정", on_click=lambda _: change_page(2)),
    ]
    
    # 비동기 태스크 실행
    page.run_task(update_time)
    
    # 레이아웃 구성
    page.add(
        ft.Column([
            ft.Row([fire_label, time_label], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row(buttons, alignment=ft.MainAxisAlignment.CENTER),
            *pages,
            status_bar
        ])
    )
    
ft.app(target=main)
