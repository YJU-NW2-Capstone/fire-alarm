import paho.mqtt.client as mqtt

class AppState:
    mqtt_broker = "43.203.127.83"
    mqtt_port = 1883
    mqtt_topics = [
        "/modbus/relay44973/out/r1",
        "/modbus/relay44973/out/r2",
        "/modbus/relay44973/out/i1",
        "/modbus/relay44973/out/i2"
    ]
    mqtt_client = None
    mqtt_handler = None

    @classmethod
    def add_mqtt_handler(cls, handler):
        cls.mqtt_handler = handler

    @classmethod
    def create_mqtt_client(cls, on_connect=None, on_message=None):
        # 기존 클라이언트가 있으면 안전하게 종료
        if cls.mqtt_client:
            cls.mqtt_client.loop_stop()
            cls.mqtt_client.disconnect()

        cls.mqtt_client = mqtt.Client()
        if on_connect:
            cls.mqtt_client.on_connect = on_connect
        if on_message:
            cls.mqtt_client.on_message = on_message

        try:
            cls.mqtt_client.connect(cls.mqtt_broker, cls.mqtt_port, 60)
            cls.mqtt_client.loop_start()
            print(f"✅ MQTT 클라이언트 연결됨: {cls.mqtt_broker}")
        except Exception as e:
            print(f"❌ MQTT 연결 실패: {e}")
            cls.mqtt_client = None

    @classmethod
    def update_broker(cls, new_broker):
        cls.mqtt_broker = new_broker
        print(f"🔄 MQTT 브로커 변경됨: {new_broker}")
        if cls.mqtt_handler:
            cls.mqtt_handler()  # 브로커 변경 이벤트 트리거