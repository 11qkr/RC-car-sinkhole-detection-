import serial
import time
import numpy as np

# --- 1. 스펙 기반 설정 ---
ARDUINO_PORT = 'COM6'     # 환경에 따라 설정 필요
BAUD_RATE = 115200
WINDOW_MEDIAN = 5         # 스펙: 5-point median
WINDOW_SMOOTH = 10        # 스펙: 저역통과 대응 이동평균
WINDOW_BASELINE = 100     # 장기 평균(1s) - 국부 급락 계산용

# 로그 분석 기반 베이스라인 (retest5 데이터 활용)
P_HEALTHY = 1250.0 
SIGMA_HEALTHY = 230.0

# --- 2. 초기화 ---
buf_l, buf_r = [], []
buf_p_sum = []

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("[FSR ANALYZER V10] 스펙 준수 모드 가동")
    print("항목: P_sum, Imbalance, Local_Drop, Score(0~1)")

    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line or line.startswith("timestamp"): continue
        
        try:
            parts = line.split(',')
            raw_l, raw_r = float(parts[1]), float(parts[2])

            # [특징 1] Median 필터링 (스펙 준수)
            buf_l.append(raw_l); buf_r.append(raw_r)
            if len(buf_l) > WINDOW_MEDIAN:
                buf_l.pop(0); buf_r.pop(0)
            f_l, f_r = np.median(buf_l), np.median(buf_r)

            # [특징 2] P_sum 및 스무딩 (저역통과 필터 대응)
            p_sum_instant = f_l + f_r
            buf_p_sum.append(p_sum_instant)
            if len(buf_p_sum) > WINDOW_BASELINE: buf_p_sum.pop(0)
            
            p_sum_smooth = np.mean(buf_p_sum[-WINDOW_SMOOTH:]) # 단기 평균
            p_sum_long = np.mean(buf_p_sum)                   # 장기 평균 (1s)

            # [특징 3] 좌우 불균형 (스펙: (L-R)/(L+R))
            imbalance = (f_l - f_r) / (f_l + f_r + 1e-6)

            # [특징 4] 국부 급락 (스펙: ΔP = P_i - median_1s)
            local_drop = p_sum_smooth - p_sum_long

            # [특징 5] 점수화 (Score FSR: 0~1)
            # 스펙: Caution(<1.5σ) -> 0.5점, Danger(<2σ or 급락) -> 1.0점
            z_score = (p_sum_smooth - P_HEALTHY) / SIGMA_HEALTHY
            
            score_fsr = 0.0
            status = "SAFE"

            if z_score < -2.0 or local_drop < -400: # Danger
                score_fsr = 1.0
                status = "🔴 DANGER"
            elif z_score < -1.5: # Caution
                score_fsr = 0.5
                status = "🟡 CAUTION"
            
            # 최종 출력 (카메라 팀이 참조할 Score 포함)
            print(f"[{status}] Score:{score_fsr:.2f} | Z:{z_score:5.2f} | Imb:{imbalance:5.2f} | Drop:{local_drop:6.1f}")

        except Exception as e:
            continue

except KeyboardInterrupt:
    print("\n 분석을 종료합니다.")
finally:
    if 'ser' in locals(): ser.close()