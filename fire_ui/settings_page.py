import flet as ft

def create_settings_page(page: ft.Page):
    def toggle_dark_mode(e):
        new_value = e.control.value
        page.theme_mode = ft.ThemeMode.DARK if new_value else ft.ThemeMode.LIGHT
        page.client_storage.set("dark_mode", "true" if new_value else "false")  # 상태 저장
        page.update()  # 전체 페이지 업데이트

    dark_mode_switch = ft.Switch(label="다크 모드", value=(page.theme_mode == ft.ThemeMode.DARK), on_change=toggle_dark_mode)

    return ft.Container(
        content=ft.Column([
            ft.Text("설정 페이지", size=20, weight=ft.FontWeight.BOLD),
            dark_mode_switch
        ]),
        padding=10
    )

def main(page: ft.Page):
    # 앱 실행 시 다크 모드 상태 불러오기
    dark_mode_enabled = page.client_storage.get("dark_mode") == "true"
    page.theme_mode = ft.ThemeMode.DARK if dark_mode_enabled else ft.ThemeMode.LIGHT

    # 페이지 레이아웃
    settings_page = create_settings_page(page)
    main_page = ft.Text("메인 페이지", size=20)

    page.add(main_page, settings_page)
    page.update()

    return
