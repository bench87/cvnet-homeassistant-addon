### cvnet wallpad homeassistant addon
cvnet 월패드와 홈어시스턴트를 연동할 수 있는 Addon 입니다.
- 제일풍경채 cvnet csh-5100 월패드를 기준으로 만들었습니다.
- 조명, 보일러, 전열교환기만 지원합니다.
- 저희 집을 기준으로 하였기에 더 많은 기능이 있는 아파트는 config 파일과 device python class를 추가하여 쉽게 기능 추가를 하실 수 있습니다.

## 빌드
``` sh
pip install pipenv
pipenv install
export MQTT_USER=your user
export MQTT_PASSWORD=your password
python3 __main.py
```
## docker build
``` sh
docker build -t cvnet-wallpad:0.1 .
docker run --net host -d -e MQTT_USER=your user -e MQTT_PASSWORD=your password cvnet-wallpad:0.1
```
## docker compose
``` yaml
 cvnet-wallpad:
    image: cvnet-wallpad:0.1
    container_name: cvnet-wallpad
    network_mode: host
    restart: unless-stopped
    environment:
      - TZ=Asia/Seoul
    volumes:
      - <<your directory>>/config:/home/appuser/wallpad/config
```
## default config
```yaml
logging:
  version: 1
  formatters:
    colored:
      (): colorlog.ColoredFormatter
      format:  '%(log_color)s%(asctime)s - %(filename)s - %(levelname)s - %(message)s'
      log_colors:
        DEBUG: white
        INFO: green
        WARNING: yellow
        ERROR: red
        CRITICAL: bold_red,bg_white
  handlers:
    console:
      class : logging.StreamHandler
      formatter: colored
      level   : INFO
      stream  : ext://sys.stdout
  loggers:
    models:
      level: DEBUG
      handlers:
      - console
      propagate: no
    devices:
      level: INFO
      handlers:
        - console
      propagate: no
    mqtt:
      level: INFO
      handlers:
        - console
      propagate: no
    ew11:
      level: INFO
      handlers:
        - console
      propagate: no
  root:
    level: INFO
    handlers:
      - console

mqtt:
  host: '192.168.0.58'
  port: 1883
  user: admin
  password: admin
  topic: 'cvnet'
ew11:
  host: '192.168.0.62'
  port: 8899

devices:
  climate:
    - name: 거실 보일러
      commands:
        cmd_heat:
          - F7 20 41 01 11 92 00 00 00 00 00 00 00 05 AA
        cmd_off:
          - F7 20 41 01 11 12 00 00 00 00 00 00 00 85 AA
        cmd_heat_ack: F7 20 01 41 91 92 1D 00 00 00 00 00 00 A2 AA
        cmd_off_ack: F7 20 01 41 91 12 1D 00 00 00 00 00 00 22 AA
        cmd_temp_ack: F7 20 01 41 91 94 1E 00 00 00 00 00 00 A5 AA
        temp_checksum: 141
      state_packet: F7 20 01 4A 81
      state_position: 5
    - name: 안방 보일러
      commands:
        cmd_heat:
          - F7 20 42 01 11 92 00 00 00 00 00 00 00 06 AA
        cmd_off:
          - F7 20 42 01 11 12 00 00 00 00 00 00 00 86 AA
        cmd_heat_ack: F7 20 01 42 91 92 1C 00 00 00 00 00 00 A2 AA
        cmd_off_ack: F7 20 01 42 91 12 1C 00 00 00 00 00 00 22 AA
        cmd_temp_ack: F7 20 01 42 91 94 1C 00 00 00 00 00 00 A4 AA
        temp_checksum: 140
      state_packet: F7 20 01 4A 81
      state_position: 7
    - name: 지율이방 보일러
      commands:
        cmd_heat:
          - F7 20 43 01 11 92 00 00 00 00 00 00 00 07 AA
        cmd_off:
          - F7 20 43 01 11 12 00 00 00 00 00 00 00 87 AA
        cmd_heat_ack: F7 20 01 21 9F 01 00 00 00 00 00 00 00 E2 AA
        cmd_off_ack: F7 20 01 43 91 12 1A 00 00 00 00 00 00 21 AA
        cmd_temp_ack: F7 20 01 43 91 93 1B 00 00 00 00 00 00 A3 AA
        temp_checksum: 139
      state_packet: F7 20 01 4A 81
      state_position: 9
    - name: 서재 보일러
      commands:
        cmd_heat:
          - F7 20 44 01 11 8e 00 00 00 00 00 00 00 04 AA
        cmd_off:
          - F7 20 44 01 11 0e 00 00 00 00 00 00 00 84 AA
        cmd_heat_ack: F7 20 01 21 9F 01 00 00 00 00 00 00 00 E2 AA
        cmd_off_ack: F7 20 01 21 9F 00 00 00 00 00 00 00 00 E1 AA
        cmd_temp_ack: F7 20 44 01 11 8F 00 00 00 00 00 00 00 05 AA
        temp_checksum: 138
      state_packet: F7 20 01 4A 81
      state_position: 11
    - name: 드레스룸 보일러
      commands:
        cmd_heat:
          - F7 20 45 01 11 92 00 00 00 00 00 00 00 09 AA
        cmd_off:
          - F7 20 45 01 11 12 00 00 00 00 00 00 00 89 AA
        cmd_heat_ack: F7 20 01 45 91 92 1C 00 00 00 00 00 00 A5 AA
        cmd_off_ack: F7 20 01 45 91 12 1D 00 00 00 00 00 00 26 AA
        cmd_temp_ack: F7 20 01 4A 81 12 1E 14 1C 13 1C 0F 18 A2 AA
        temp_checksum: 137
      state_packet: F7 20 01 4B 81
      state_position: 5
  fan:
    - name: 전열 교환기
      commands:
        cmd_on:
          - F7 20 71 01 11 01 01 01 00 00 00 00 00 A6 AA
        cmd_off:
          - F7 20 71 01 11 00 00 00 00 00 00 00 00 A3 AA
        cmd_on_ack:  F7 20 01 71 91 01 01 01 00 00 00 00 00 26 AA
        cmd_off_ack: F7 20 01 71 91 00 01 00 00 00 00 00 00 24 AA
        cmd_low: F7 20 71 01 11 01 01 01 00 00 00 00 00 A6 AA
        cmd_medium: F7 20 71 01 11 01 01 02 00 00 00 00 00 A7 AA
        cmd_high: F7 20 71 01 11 01 01 03 00 00 00 00 00 A8 AA
      state_packet: F7 20 01 71 81
      state_position: 7

  switch:
    - name: 거실 메인 조명1
      commands:
        cmd_on:
        - F7 20 21 01 11 03 00 00 00 00 00 00 00 56 AA
        cmd_off:
        - F7 20 21 01 11 00 00 00 00 00 00 00 00 53 AA
        cmd_on_ack: F7 20 01 21 9F 01 00 00 00 00 00 00 00 E2 AA
        cmd_off_ack: F7 20 01 21 9F 00 00 00 00 00 00 00 00 E1 AA
      state_packet: F7 20 01 21 81
      state_position: 5

    - name: 거실 메인 조명2
      commands:
        cmd_on:
        - F7 20 21 01 12 01 00 00 00 00 00 00 00 55 AA
        cmd_off:
        - F7 20 21 01 12 00 00 00 00 00 00 00 00 54 AA
        cmd_on_ack: F7 20 01 21 9F 01 01 00 00 00 00 00 00 E3 AA
        cmd_off_ack: F7 20 01 21 9F 01 00 00 00 00 00 00 00 E2 AA
      state_packet: F7 20 01 21 81
      state_position: 6
    - name: 거실 메인 복도 조명
      key: light3
      commands:
        cmd_on:
        - F7 20 21 01 13 01 00 00 00 00 00 00 00 56 AA
        cmd_off:
        - F7 20 21 01 13 00 00 00 00 00 00 00 00 55 AA
        cmd_on_ack: F7 20 01 21 9F 00 00 01 00 00 00 00 00 E2 AA
        cmd_off_ack: F7 20 01 21 9F 00 00 00 00 00 00 00 00 E1 AA
      state_packet: F7 20 01 21 81
      state_position: 7
    - name: 안방 메인 조명
      commands:
        cmd_on:
          - F7 20 22 01 11 01 00 00 00 00 00 00 00 55 AA
        cmd_off:
          - F7 20 22 01 11 00 00 00 00 00 00 00 00 54 AA
        cmd_on_ack: F7 20 01 22 9F 01 00 00 00 00 00 00 00 E3 AA
        cmd_off_ack: F7 20 01 22 9F 00 00 00 00 00 00 00 00 E2 AA
      state_packet: F7 20 01 22 81
      state_position: 5
    - name: 엘리베이터
      commands:
        cmd_on:
          - F7 20 01 E1 81 02 00 01 00 00 02 31 33 EC AA
          - F7 20 01 E1 81 02 00 01 00 00 04 30 38 F2 AA
        cmd_off:
          - F7 20 01 E1 81 02 00 01 00 00 02 31 33 EC AA
          - F7 20 01 E1 81 02 00 01 00 00 04 30 38 F2 AA
      state_packet: F7 20 01 22 81
      state_position: 5

```
# 참조
아래 github repository를 참고하지 않았다면 저는 만들지 못했습니다.
- [zooil/wallpad](https://github.com/zooil/wallpad)
- [vifrost/kocom.py](https://github.com/vifrost/kocom.py/blob/master/kocom.py)
