import flet as ft

def create_situation_page():
    return ft.Container(
        content=ft.Column([
            ft.Text("메인 페이지", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("여기에 메인 페이지 내용을 추가하세요.")
        ]),
        padding=10
    )
