import flet as ft

def create_log_page(page: ft.Page):
    return ft.Container(
        content=ft.Column([
            ft.Text("로그 페이지", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("여기에 로그 페이지 내용을 추가하세요.")
        ]),
        padding=10
    )
    
    async def update_signal():
        # 필요하다면 주기적인 업데이트 코드를 작성하거나 간단히 page.update()를 호출
        while True:
            page.update()
            await asyncio.sleep(1)
    
    container.update_signal = update_signal  # 비동기 함수 할당
    return container
