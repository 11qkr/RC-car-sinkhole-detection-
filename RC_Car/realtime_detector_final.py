import serial
import time
import numpy as np
import json  

# --- 1. 설정값 ---
ARDUINO_PORT = 'COM6' # 본인 환경에 맞게 수정
BAUD_RATE = 115200
WINDOW_SIZE = 5 

# 임계값 (데모 성공 수치 반영)
P_THRESHOLD_CAUTION = 1100.0 
P_THRESHOLD_DANGER = 700.0
P_NORMAL = 1500.0 # 기준값

# --- 변수 초기화 ---
buffer_p_sum = []

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(" [INTEGRATION MODE] FSR 노면 분석 엔진 가동 중...")

    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line or line.startswith("timestamp"): continue
        
        try:
            parts = line.split(',')
            raw_l, raw_r = float(parts[1]), float(parts[2])
            p_sum_raw = raw_l + raw_r

            buffer_p_sum.append(p_sum_raw)
            if len(buffer_p_sum) > 20: buffer_p_sum.pop(0) # 비교를 위해 20개 유지
            
            p_avg = np.mean(buffer_p_sum[-WINDOW_SIZE:]) # 현재 평균
            p_long = np.mean(buffer_p_sum)               # 장기 평균
            
            # [특징점 계산 - 스펙 준수]
            local_drop = p_avg - p_long                  # 급락 수치 (Drop)
            imbalance = (raw_l - raw_r) / (raw_l + raw_r + 1e-6) # 좌우 불균형

            # [상태 및 점수 판정]
            status = "SAFE"
            score = 0.0

            if p_avg < P_THRESHOLD_DANGER:
                status = "DANGER"
                score = 1.0
            elif p_avg < P_THRESHOLD_CAUTION:
                status = "CAUTION"
                score = 0.5

            # --- 2. [핵심] 다른 팀을 위한 데이터 전달 (Handover) ---
            result = {
                "status": status,
                "score_fsr": score,
                "p_sum": round(p_avg, 1),
                "imbalance": round(imbalance, 2),
                "local_drop": round(local_drop, 1)
            }

            # road_result.json 파일에 실시간 저장 (ai 파트에서 읽는 부분)
            with open("road_result.json", "w") as f:
                json.dump(result, f)

            # 내 터미널 확인용
            print(f"[{status}] Score:{score} | Imb:{imbalance:5.2f} | P_avg:{p_avg:7.1f}")

        except: continue

except KeyboardInterrupt:
    print("\n 종료.")
finally:
    if 'ser' in locals(): ser.close()