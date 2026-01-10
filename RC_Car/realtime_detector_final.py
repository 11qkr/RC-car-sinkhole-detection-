import serial
import time
import numpy as np
import json

ARDUINO_PORT = 'COM6' 
BAUD_RATE = 115200
WINDOW_SIZE = 5 

# 실측 보정값
P_NORMAL = 1500.0   # 정상
P_CAUTION = 1100.0  # 주의 (1100 미만부터 점수 상승)
P_DANGER = 700.0    # 위험 (700 미만부터 점수 1.0 고정)

buffer_p_sum = []

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(" [INTEGRATION] 수치 보정 유지 + 0~1 Score 모드")

    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line or line.startswith("timestamp"): continue
        
        try:
            parts = line.split(',')
            p_sum_raw = float(parts[1]) + float(parts[2])

            # 5개 csv 파일 데이터 평균 필터
            buffer_p_sum.append(p_sum_raw)
            if len(buffer_p_sum) > WINDOW_SIZE: buffer_p_sum.pop(0)
            p_avg = np.mean(buffer_p_sum)

            # --- 0.0~1.0으로 변환 ---
            if p_avg >= P_NORMAL:
                score_fsr = 0.0
            elif p_avg >= P_CAUTION:
                # 1100 ~ 1500 사이는 점수 0.0 ~ 0.5
                score_fsr = np.interp(p_avg, [P_CAUTION, P_NORMAL], [0.5, 0.0])
            elif p_avg >= P_DANGER:
                # 700 ~ 1100 사이는 점수 0.5 ~ 1.0
                score_fsr = np.interp(p_avg, [P_DANGER, P_CAUTION], [1.0, 0.5])
            else:
                score_fsr = 1.0

            # 상태 판정 
            if score_fsr >= 1.0: status = "🔴 [DANGER]"
            elif score_fsr >= 0.5: status = "🟡 [CAUTION]"
            else: status = "🟢 [SAFE]"

            # 결과 데이터
            result = {"status": status, "score_fsr": round(float(score_fsr), 2)}
            with open("road_result.json", "w") as f:
                json.dump(result, f)

            # 출력 화면
            print(f"P_avg:{p_avg:7.1f} | Score:{score_fsr:4.2f} | {status}")

        except: continue

except KeyboardInterrupt:
    print("\n 종료.")
finally:
    if 'ser' in locals(): ser.close()
