# 🐠 관상어용 스마트 어항 시스템 IoT

Raspberry Pi 기반 IoT 시스템으로 수온 및 수질 측정과 원격 먹이 급여, 환수 제어 기능을 제공합니다.
또한 MediaMTX와 FFmpeg를 활용하여 카메라 영상을 AWS EC2 서버로 중계하고 사용자가 모바일 애플리케이션에서 실시간으로 어항을 확인할 수 있도록 지원합니다.

🔗 **통합 프로젝트 저장소:** [관상어용 스마트 어항 시스템](https://github.com/ksw2003/fishapp_main)

### 📁 프로젝트 구조

```text
streaming/
├── mediamtx.yml        # MediaMTX 영상 송출 설정
├── mediamtx.service    # MediaMTX 자동 실행 서비스
├── aws-relay.service   # AWS 영상 중계 자동 실행 서비스
├── relay.sh            # FFmpeg 기반 RTSP 영상 중계
└── .env.example        # AWS 연결 환경 변수 예시

iot/
├── venv/                 # Python 가상환경 (Git 제외)
├── .env                  # 환경 변수 설정 파일 (Git 제외)
├── .env.example          # 환경 변수 설정 예시
├── requirements.txt      # Python 패키지 및 라이브러리 의존성 목록
├── config.py             # 공통 환경 변수 및 서버 설정 관리
├── feeder.py             # 먹이 급여 모터 제어
├── iot_ws.py             # 서버와 실시간 WebSocket 통신
├── main.py               # IoT 시스템 실행 및 전체 기능 관리
├── sensorAPI.py          # 센서 데이터 서버 전송
├── temperature.py        # 수온 센서 측정
├── waterPump.py          # 환수 펌프 제어
└── waterQuality.py       # 수질 데이터 측정 및 처리
```

### 🛠 기술 스택 //피더모터 추가해야함
| 기술 스택 | 설명|
|:---:|:---:|
| Raspberry Pi 3 Model B (1GB RAM) | IoT 센서 및 장치 제어, 실시간 영상 스트리밍 |
| MicroSDHC PRO 16GB | Raspberry Pi 운영체제 및 데이터 저장 |
| MCP3008-I/P | 아날로그 센서 데이터 디지털 변환 |
| SZH-RLBG-042 | 2채널 5V 릴레이 모듈 |
| DS18B20 | 어항 수온 측정 |
| SZH-TSM002 | TDS 기반 수질 측정 |
| Float Switch | 어항 수위 감지 |
| Arduino Water Pump | 어항 환수를 위한 워터 펌프 |
| MediaMTX | RTSP 기반 실시간 영상 스트리밍 |
| FFmpeg | Raspberry Pi에서 AWS EC2로 영상 중계 |
| systemd | 영상 송출 및 중계 서비스 자동 실행 |

### ⚙️ 실행 방법
### 📟 IoT
#### 1️⃣ 프로젝트 클론

```bash
git clone https://github.com/ksw2003/fishapp_iot.git
cd fishapp_iot
```

#### 2️⃣ Python 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ 필수 패키지 설치

```bash
pip install -r requirements.txt
```

#### 4️⃣ 환경 변수 설정

프로젝트 루트 디렉터리에 `.env` 파일을 생성하고 서버 연결 정보를 설정합니다.

```env
SERVER_URL=<BACKEND_SERVER_URL>
SERVER_WS=<BACKEND_WS_SERVER_URL>
DEVICE_ID=SS501
```

#### 5️⃣ IoT 프로그램 실행

가상환경이 활성화된 상태에서 메인 프로그램을 실행합니다.

```bash
python3 main.py
```

#### 6️⃣ 프로그램 종료

실행 중인 터미널에서 `Ctrl + C`를 입력하여 프로그램을 종료합니다.

### 🔗 IoT 연동 방식

Raspberry Pi와 AWS EC2 백엔드 서버 간 HTTP API 및 WebSocket 통신을 통해 연동합니다. HTTP API를 통해 수온 및 수질 데이터를 서버로 전송하고, WebSocket을 통해 먹이 급여 및 환수 명령을 수신하여 IoT 장치를 제어합니다.

---

### 🎥 실시간 영상 송출
#### 1️⃣ MediaMTX 및 FFmpeg 설치

Raspberry Pi 환경에 MediaMTX와 FFmpeg를 설치합니다.

MediaMTX는 [공식 GitHub 저장소](https://github.com/bluenviron/mediamtx)에서 다운로드할 수 있습니다.

#### 2️⃣ 설정 파일 배치

| 파일 | Raspberry Pi 경로 |
|---|---|
| `mediamtx.yml` | `/home/fish/mediamtx.yml` |
| `mediamtx.service` | `/etc/systemd/system/mediamtx.service` |
| `aws-relay.service` | `/etc/systemd/system/aws-relay.service` |
| `relay.sh` | `/home/fish/aws-relay/relay.sh` |
| `.env` | `/home/fish/aws-relay/.env` |

서비스 파일에 지정된 사용자 이름과 실행 경로는 Raspberry Pi 환경에 맞게 수정해야 합니다.

#### 3️⃣ 환경 변수 설정

`streaming/.env.example`을 참고하여 `/home/fish/aws-relay/.env` 파일을 생성합니다.

```dotenv
AWS_PUBLIC_IP=YOUR_AWS_PUBLIC_IP
RTSP_USER=fishpublisher
RTSP_PASSWORD=YOUR_RTSP_PASSWORD
```

AWS EC2의 MediaMTX 서버에 설정된 RTSP 인증 정보를 입력합니다.

### 📡 영상 중계 방식

MediaMTX를 통해 Raspberry Pi 카메라 영상을 RTSP로 송출하고, FFmpeg를 이용해 AWS EC2 서버로 중계합니다. 영상 송출이 정체되면 자동으로 재시작하도록 구성했습니다.
