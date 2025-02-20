import flet as ft
import os

def create_main_page():
    # 현재 스크립트의 디렉토리를 기준으로 상대 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "..", "resource", "main.jpg")
    
    # 이미지 파일이 존재하는지 확인
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return ft.Text("이미지를 찾을 수 없습니다.")

    image = ft.Image(
        src=image_path,
        width=500,
        height=500,
    )
    
    return ft.Container(
        content=ft.Column([
            image
        ], alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        expand=True
    )
