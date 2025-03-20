import flet as ft
import paho.mqtt.client as mqtt
from datetime import datetime
import os
import asyncio

# 로그 저장 파일
LOG_FILE = "alarm_history.txt"

# 전역 변수들
fire_count = 0
fire_test_count = 0
alarm_history_records = []  # 경보 이력 전역 리스트
current_audio = None      # 현재 재생 중인 알림음 객체 저장

# Flet 페이지 인스턴스 전역 변수 (상황페이지에서 사용)
page_instance = None
stop_button = None       # "확인" 버튼 객체

def load_logs():
    """파일에서 기존 로그를 불러오되, 이전 데이터는 초기화합니다."""
    global alarm_history_records, fire_count, fire_test_count
    alarm_history_records.clear()
    fire_count = 0
    fire_test_count = 0
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                record = line.strip()
                if record:
                    alarm_history_records.append(record)
                    if "실제 화재 발생" in record:
                        fire_count += 1
                    elif "테스트 화재 발생" in record:
                        fire_test_count += 1

def save_logs():
    """현재 로그를 파일에 저장합니다."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for record in alarm_history_records:
            f.write(record + "\n")

def fire_alarm_trigger(is_test):
    """화재 감지 시 실행 (실제와 테스트 구분)"""
    global page_instance, current_audio, fire_count, fire_test_count
    if page_instance:
        if page_instance.window.minimized:
            page_instance.window.minimized = False

        # 상태 텍스트 업데이트
        fire_status_text.value = "🔥 화재 감지됨! 🔥" if not is_test else "⚠️ 테스트 화재 경보! ⚠️"
        fire_status_text.color = "red" if not is_test else "orange"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"🚨 [경보] {timestamp} - {'실제 화재 발생' if not is_test else '테스트 화재 발생'}!"

        if alert_message not in alarm_history_records:
            alarm_history_records.append(alert_message)
            save_logs()
            if not is_test:
                fire_count += 1
            else:
                fire_test_count += 1

        if current_audio is None:
            play_alert_sound()

        page_instance.update()

def play_alert_sound():
    """화재 경보 음성을 재생합니다."""
    global page_instance, current_audio, stop_button
    if page_instance:
        current_audio = ft.Audio(src="fire_ui\\source\\main_sound.mp3", autoplay=True)
        page_instance.overlay.append(current_audio)
        stop_button.visible = True
        page_instance.update()

def stop_alert_sound(e):
    """알림 음성을 중지합니다. (버튼은 항상 보임)"""
    global page_instance, current_audio, stop_button
    if page_instance and current_audio:
        page_instance.overlay.remove(current_audio)
        current_audio = None
        page_instance.update()

def create_situation_page(page: ft.Page):
    """화재 감지 상황 페이지 UI를 구성하여 반환합니다.
       - 상황 페이지로 진입할 때마다 load_logs()를 호출하여 기존 경보 이력을 새롭게 불러오며,
         중복 기록을 방지합니다.
       - 추가로, 비동기 태스크를 통해 1초마다 전역 경보 이력 기록(alarm_history_records)을
         ListView에 반영하여 실시간 업데이트되도록 합니다.
    """
    global page_instance, fire_status_text, alarm_history, stop_button
    global fire_count, fire_test_count, alarm_history_records

    page_instance = page
    page.title = "화재 감지 시스템 - 상황 페이지"

    fire_status_text = ft.Text("현재 감지된 화재 없음", size=20, weight="bold", color="green")
    alarm_history = ft.ListView(expand=True, spacing=10, padding=10)

    # 기존 경보 이력 복원 (load_logs()에서 전역 기록을 초기화하고 새로 불러옴)
    load_logs()
    alarm_history.controls.clear()
    for record in alarm_history_records:
        color = "red" if "실제" in record else "orange"
        alarm_history.controls.append(ft.Text(record, size=16, color=color))

    stop_button = ft.ElevatedButton(
        text="확인", 
        on_click=stop_alert_sound,
        visible=True  # 항상 보임
    )

    test_fire_button = ft.ElevatedButton(
        text="테스트 화재 발생", 
        on_click=lambda e: fire_alarm_trigger(True)
    )

    content = ft.Column(
        controls=[
            ft.Text("📌 실시간 화재 감지 현황", size=24, weight="bold"),
            fire_status_text,
            stop_button,
            test_fire_button,
            ft.Text(f"🔥 실제 화재 발생 횟수: {fire_count}", size=16, color="red"),
            ft.Text(f"⚠️ 테스트 화재 발생 횟수: {fire_test_count}", size=16, color="orange"),
            ft.Text("📜 경보 이력", size=20, weight="bold"),
            alarm_history,
        ],
        spacing=20
    )

    async def update_alarm_history():
        while True:
            # 만약 alarm_history(ListView)가 현재 페이지에 붙어있다면 업데이트
            if alarm_history and alarm_history.page is not None:
                alarm_history.controls.clear()
                for record in alarm_history_records:
                    color = "red" if "실제" in record else "orange"
                    alarm_history.controls.append(ft.Text(record, size=16, color=color))
                page.update()
            await asyncio.sleep(1)  # 1초마다 업데이트

    # 여기서 비동기 태스크를 시작합니다.
    page.run_task(update_alarm_history)

    return content
