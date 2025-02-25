import flet as ft

def create_settings_page(page: ft.Page):
    def toggle_dark_mode(e):
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        page.update()  # 변경 사항 반영

    dark_mode_switch = ft.Switch(label="다크 모드", value=False, on_change=toggle_dark_mode)

    return ft.Container(
        content=ft.Column([
            ft.Text("설정 페이지", size=20, weight=ft.FontWeight.BOLD),
            dark_mode_switch
        ]),
        padding=10
    )
