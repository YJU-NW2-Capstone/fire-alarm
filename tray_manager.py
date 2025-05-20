# import os
# import sys
# import subprocess
# import psutil
# import winreg
# from PIL import Image
# from pystray import Icon, MenuItem, Menu

# APP_NAME = "FireAlarmTray"  # 레지스트리 Run 키에 등록할 이름
# ICON_LABEL = "FireAlarmTray"  # 트레이 툴팁
# RESOURCE_DIR = "source"
# FLET_EXE = "Fire_ui.exe"  # 빌드된 Flet UI exe 이름

# RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
# TRAY_RUNNING = False  # 트레이 중복 방지 플래그

# def resource_path(relative_path):
#     """PyInstaller 및 개발 환경에서 실행 파일 경로 처리"""
#     if hasattr(sys, "_MEIPASS"):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)

# def register_startup():
#     """로그온 시 tray_launcher.exe만 자동 실행되도록 레지스트리 등록"""
#     exe_path = sys.executable  # tray_launcher.exe 자신
#     try:
#         with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
#             winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
#         print(f"[INFO] 시작 프로그램에 {APP_NAME} 등록 성공")
#     except Exception as e:
#         print(f"[ERROR] 시작 프로그램 등록 실패: {e}")

# def unregister_startup():
#     """시작 프로그램에서 tray_launcher.exe 제거"""
#     try:
#         with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
#             winreg.DeleteValue(key, APP_NAME)
#         print(f"[INFO] 시작 프로그램에서 {APP_NAME} 제거 성공")
#     except Exception as e:
#         print(f"[ERROR] 시작 프로그램 해제 실패: {e}")

# def is_app_running():
#     """Fire_ui.exe 실행 여부 확인"""
#     for proc in psutil.process_iter(['name']):
#         if proc.info['name'] and proc.info['name'].lower() == FLET_EXE.lower():
#             return True
#     return False

# def run_app(icon=None, item=None):
#     """Fire_ui.exe 실행"""
#     if is_app_running():
#         print("[INFO] 앱이 이미 실행 중입니다.")
#         return

#     exe_path = resource_path(FLET_EXE)  # Fire_ui.exe 경로
#     try:
#         subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
#         print("[INFO] 앱 실행 성공")
#     except FileNotFoundError:
#         print(f"[ERROR] 실행 파일이 존재하지 않습니다: {exe_path}")
#     except Exception as e:
#         print(f"[ERROR] 앱 실행 실패: {e}")

# def exit_all(icon, item):
#     """트레이와 앱을 포함하여 모든 종료"""
#     global TRAY_RUNNING
#     TRAY_RUNNING = False

#     # 실행 중인 Fire_ui.exe 종료
#     try:
#         for proc in psutil.process_iter(['name', 'pid']):
#             if proc.info['name'] and proc.info['name'].lower() == FLET_EXE.lower():
#                 print(f"[INFO] 프로세스 종료 시도: {proc.info['name']} (PID: {proc.info['pid']})")
#                 proc.kill()  # 강제 종료 시도
#                 print(f"[INFO] 프로세스 강제 종료 성공: {proc.info['pid']}")
#     except Exception as e:
#         print(f"[ERROR] 프로세스 종료 실패: {e}")

#     # Windows에서 taskkill 명령어로 강제 종료
#     try:
#         subprocess.run(
#             ["taskkill", "/f", "/im", FLET_EXE],
#             check=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
#         print("[INFO] Windows 명령어로 프로세스 강제 종료 성공")
#     except subprocess.CalledProcessError as e:
#         print(f"[ERROR] Windows 명령어로 프로세스 종료 실패: {e}")

#     # 트레이 종료
#     icon.stop()
#     print("[INFO] 트레이 종료 완료")
#     os._exit(0)

# def create_tray():
#     """트레이 아이콘 생성 및 실행"""
#     global TRAY_RUNNING
#     if TRAY_RUNNING:
#         print("[INFO] 트레이 이미 실행 중")
#         return

#     TRAY_RUNNING = True
#     icon_path = resource_path(os.path.join(RESOURCE_DIR, "icon.ico"))
#     image = Image.open(icon_path)

#     menu = Menu(
#         MenuItem("앱 실행", run_app),
#         MenuItem("종료", exit_all)
#     )

#     tray = Icon(ICON_LABEL, image, ICON_LABEL, menu)
#     tray.run()

# def main():
#     register_startup()   # 윈도우 시작 시 tray_launcher.exe 자동 기동
#     create_tray()        # 트레이 에이전트 실행
#     run_app()            # 트레이 실행과 함께 앱 실행

# if __name__ == "__main__":
#     main()