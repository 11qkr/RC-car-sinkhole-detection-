import serial
import time
import numpy as np

# --- 1. 장애물 데이터(r2, r3) 기반 최적 설정 ---
ARDUINO_PORT = 'COM6' 
BAUD_RATE = 115200

# 필터 크기를 아주 작게 -> 포트홀의 순간 하중 하락 포착.
WINDOW_SIZE = 5 

# [장애물 감지 기준 수치 - 직접 제어]
# 정상 하중: 1500 근처
# 주의(Sponge): 1000 이하로 떨어지면 감지
# 위험(Pothole): 600 이하로 떨어지면 감지
P_THRESHOLD_CAUTION = 1100.0 
P_THRESHOLD_DANGER = 700.0

# --- 변수 초기화 ---
buffer_p_sum = []

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(" [DEMO MODE] 장애물 정밀 감지 시작")
    print(f"기준: Danger < {P_THRESHOLD_DANGER} | Caution < {P_THRESHOLD_CAUTION}\n")

    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line or line.startswith("timestamp"): continue
        
        try:
            parts = line.split(',')
            p_sum_raw = float(parts[1]) + float(parts[2])

            # 1. 초고속 필터링 (5개 데이터 평균)
            buffer_p_sum.append(p_sum_raw)
            if len(buffer_p_sum) > WINDOW_SIZE:
                buffer_p_sum.pop(0)
            
            p_avg = np.mean(buffer_p_sum)

            # 2. 직관적인 수치 기반 판정 (Z-score 대신 절대 수치 사용)
            if p_avg < P_THRESHOLD_DANGER:
                status = "🔴 [DANGER: POTHOLE]"
            elif p_avg < P_THRESHOLD_CAUTION:
                status = "🟡 [CAUTION: SPONGE]"
            else:
                status = "🟢 [SAFE]"

            # 실시간 출력
            print(f"P_avg:{p_avg:7.1f} | Raw:{p_sum_raw:6.1f} | {status}")

        except: continue

except KeyboardInterrupt:
    print("\n 종료.")
finally:
    if 'ser' in locals(): ser.close()