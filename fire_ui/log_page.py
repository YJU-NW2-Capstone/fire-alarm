import flet as ft
import paho.mqtt.client as mqtt

def create_log_page(page: ft.Page):
    log_container = ft.Column(scroll=ft.ScrollMode.AUTO)

    def add_log(message):
        log_entry = ft.Text(message, size=18)
        log_container.controls.append(log_entry)
        page.update()

    container = ft.Container(
        content=ft.Column([
            ft.Text("로그 페이지", size=20, weight=ft.FontWeight.BOLD),
            log_container
        ]),
        padding=10,
        expand=True
    )
    
    container.add_log = add_log  # 외부에서 로그 추가 가능하도록 설정
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            add_log("MQTT 연결 성공")
            topics = [
                "/modbus/relay44973/out/lwt_availability",
                "/modbus/relay44973/out/r1",
                "/modbus/relay44973/out/r2",
                "/modbus/relay44973/out/i1",
                "/modbus/relay44973/out/i2",
                "/modbus/relay44973/out/ip",
                "/modbus/relay44973/out/sn",
                "/modbus/relay44973/out/hw_version",
                "/modbus/relay44973/out/sw_version",
            ]
            for topic in topics:
                client.subscribe(topic)
        else:
            add_log(f"MQTT 연결 실패: 코드 {rc}")
    
    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        add_log(f"[ {topic} ] {payload}")
    
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect("10.40.1.58", 1883, 60)
        mqtt_client.loop_start()
    except Exception as e:
        add_log(f"MQTT 연결 오류: {e}")
    
    return container
