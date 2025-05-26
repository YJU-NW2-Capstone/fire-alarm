# import flet as ft
# from app_state import AppState

# # 층 이름과 이미지 파일 매핑 (예시 경로)
# FLOORS = {
#     "1층": "source/floor1.jpg",
#     "2층": "source/floor2.jpg",
#     "3층": "source/floor3.jpg",
#     "4층": "source/floor4.jpg",
#     "5층": "source/floor5.jpg"
# }

# # 센서 정보: topic, (x, y) 위치 (이미지 기준 상대 위치)
# SENSOR_POSITIONS = {
#     "1층": {
#         "sensor/1": (0.2, 0.3),
#         "sensor/2": (0.6, 0.4),
#     },
#     "2층": {
#         "sensor/3": (0.3, 0.5),
#     },
#     "3층": {
#         "sensor/4": (0.4, 0.6),
#     },
#     "4층": {
#         "sensor/5": (0.5, 0.2),
#     },
#     "5층": {
#         "sensor/6": (0.6, 0.3),
#     },
# }

# # 센서 상태 저장 (ON = 정상, OFF = 화재)
# sensor_states = {}

# def create_map_page(page: ft.Page):
#     selected_floor = ft.Text("1층", size=24, weight="bold")
#     image_container = ft.Stack(expand=True)
#     button_row = ft.Row(spacing=10)
    
#     def load_floor(floor_name):
#         selected_floor.value = floor_name
#         image_container.controls.clear()

#         # 배경 이미지 추가
#         image = ft.Image(src=FLOORS[floor_name], expand=True, fit=ft.ImageFit.CONTAIN)
#         image_container.controls.append(image)

#         # 센서 점 추가
#         if floor_name in SENSOR_POSITIONS:
#             for topic, (x, y) in SENSOR_POSITIONS[floor_name].items():
#                 color = "red" if sensor_states.get(topic) == "OFF" else "green"
#                 dot = ft.Container(
#                     width=15,
#                     height=15,
#                     bgcolor=color,
#                     border_radius=15,
#                     left=ft.transform.scale(x),
#                     top=ft.transform.scale(y),
#                     alignment=ft.alignment.center,
#                 )
#                 image_container.controls.append(dot)

#         page.update()

#     # 버튼 생성
#     for floor_name in FLOORS.keys():
#         btn = ft.ElevatedButton(text=floor_name, on_click=lambda e, f=floor_name: load_floor(f))
#         button_row.controls.append(btn)

#     # MQTT 메시지 수신 시 센서 상태 갱신
#     def on_mqtt_message(client, userdata, msg):
#         try:
#             topic = msg.topic
#             payload = msg.payload.decode("utf-8")
#             print(f"[MAP] 수신: {topic} → {payload}")
#             if topic in sum(SENSOR_POSITIONS.values(), {}).keys():
#                 sensor_states[topic] = payload
#                 load_floor(selected_floor.value)  # 현재 층 다시 로딩
#         except Exception as e:
#             print(f"[MAP] 오류: {e}")

#     # 브로커 변경 시 MQTT 핸들러 등록
#     def on_broker_change():
#         AppState.create_mqtt_client(on_connect=None, on_message=on_mqtt_message)

#     AppState.add_mqtt_handler(on_broker_change)

#     if not hasattr(AppState, 'mqtt_client') or AppState.mqtt_client is None:
#         AppState.create_mqtt_client(on_connect=None, on_message=on_mqtt_message)

#     # 초기 1층 로딩
#     load_floor("1층")

#     return ft.Column([
#         selected_floor,
#         button_row,
#         ft.Container(image_container, expand=True)
#     ], expand=True)
