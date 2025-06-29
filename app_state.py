import paho.mqtt.client as mqtt
import threading

class AppState:

    mqtt_broker = "54.180.238.32"
    mqtt_port = 1883
    mqtt_topics = [
        "/modbus/relay44973/out/r1",
        "/modbus/relay44973/out/r2",
        "/modbus/relay44973/out/i1",
        "/modbus/relay44973/out/i2",
        "esp32/302"
    ]
    mqtt_client = None
    mqtt_handlers = []
    _handler_lock = threading.Lock()  # 스레드 안전성
    alarm_active = False
    # current_fire_status = False

    @classmethod
    def add_mqtt_handler(cls, handler):
        with cls._handler_lock:
            if handler not in cls.mqtt_handlers:
                cls.mqtt_handlers.append(handler)

    @classmethod
    def remove_mqtt_handler(cls, handler):
        with cls._handler_lock:
            if handler in cls.mqtt_handlers:
                cls.mqtt_handlers.remove(handler)

    @classmethod
    def create_mqtt_client(cls):
        if cls.mqtt_client:
            try:
                cls.mqtt_client.loop_stop()
                cls.mqtt_client.disconnect()
            except Exception as e:
                print(f"MQTT 클라이언트 정리 중 오류: {e}")
        # 고유 client_id, 프로토콜 버전, LWT, (옵션) 인증 정보 적용
        cls.mqtt_client = mqtt.Client(
            client_id="FireAlarmSystemClient",
            protocol=mqtt.MQTTv311  # 또는 MQTTv5
        )
        # 인증이 필요하다면 아래 주석 해제
        # cls.mqtt_client.username_pw_set("username", "password")
        cls.mqtt_client.will_set("system/status", "offline", qos=1, retain=True)
        cls.mqtt_client.on_connect = cls.on_connect
        cls.mqtt_client.on_message = cls.on_message
        cls.mqtt_client.on_disconnect = cls.on_disconnect
        try:
            cls.mqtt_client.connect(cls.mqtt_broker, cls.mqtt_port, 60)
            cls.mqtt_client.loop_start()
            print(f"✅ MQTT 클라이언트 연결됨: {cls.mqtt_broker}")
        except Exception as e:
            print(f"❌ MQTT 연결 실패: {e}")
            cls.mqtt_client = None

    @classmethod
    def on_connect(cls, client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT 연결 성공")
            for topic in cls.mqtt_topics:
                client.subscribe(topic, qos=1)
                print(f"🔔 MQTT 토픽 구독: {topic}")
            # 온라인 상태를 브로커에 알림
            client.publish("system/status", "online", qos=1, retain=True)
        else:
            print(f"❌ MQTT 연결 실패 코드: {rc}")

    @classmethod
    def on_disconnect(cls, client, userdata, rc):
        print(f"❌ MQTT 연결 끊김 (코드: {rc}). 재연결 시도...")
        # 비정상 종료 시 자동 재연결
        if rc != 0:
            cls.create_mqtt_client()

    @classmethod
    def on_message(cls, client, userdata, msg):
        with cls._handler_lock:
            for handler in cls.mqtt_handlers:
                try:
                    handler(client, userdata, msg)
                except Exception as e:
                    print(f"핸들러 실행 오류: {e}")

    @classmethod
    def update_broker(cls, new_broker):
        cls.mqtt_broker = new_broker
        print(f"🔄 MQTT 브로커 변경됨: {new_broker}")
        cls.create_mqtt_client()  # 브로커 변경 시 재연결
