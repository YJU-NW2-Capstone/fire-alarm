import flet as ft
import asyncio

def create_main_page(page: ft.Page):
    image_path = "fire_ui\source\찐메인.png"

    safety_rules = ft.Container(
        content=ft.Column([
            ft.Text("화재 안전 수칙", size=18, weight=ft.FontWeight.BOLD, color="black"),
            ft.Text("1. 탈출경로, 소화기 위치확인", size=14, weight=ft.FontWeight.BOLD, color="black"),
            ft.Text("2. 소화기 사용법과 심폐소생술 알아두기", size=14, weight=ft.FontWeight.BOLD, color="black"),
            ft.Text("3. 대피후 집결장소 알아두기", size=14, weight=ft.FontWeight.BOLD, color="black"),
            ft.Text("4. 불이 발생할시 크게 소리지르고 119신고하기", size=14, weight=ft.FontWeight.BOLD, color="black"),
            ft.Text("5. 불이 끄기 어려울시 신속하게 대피할 것", size=14, weight=ft.FontWeight.BOLD, color="black"),
            ft.Text("6. 대피할 시 코와 입을 막고, 자세를 낮추고 탈출하기", size=14, weight=ft.FontWeight.BOLD, color="black"),
        ], tight=True),
        padding=10,
        border=ft.border.all(1, ft.colors.GREY_400),
        border_radius=10,
        bgcolor="#a0a0a0",
    )

    try:
        image = ft.Image(
            src=image_path,
            width=300,
            height=200,
            fit=ft.ImageFit.CONTAIN
        )
    except Exception as e:
        print(f"이미지 로드 오류: {e}")
        image = ft.Container()  # 이미지 로드 실패 시 빈 컨테이너 반환

    container = ft.Container(
        content=ft.Column([
            ft.Container(height=50),
            ft.Row([image], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Row([safety_rules], alignment=ft.MainAxisAlignment.END)
        ], alignment=ft.MainAxisAlignment.START, spacing=10),
        padding=ft.padding.only(top=20, right=20, left=20),
        expand=True,
        alignment=ft.alignment.center

    )

    # 업데이트 함수: 필요 시 사용 (비동기 함수로 변경)
    async def update_signal():
        while True:
            page.update()
            await asyncio.sleep(1)

    container.update_signal = update_signal

    return container
