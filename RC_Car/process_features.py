import pandas as pd
import numpy as np
import os

def analyze_new_data():
    # 1. 기준 설정 (정상주행 retest5 파일 사용) // 데이터 파일명에 맞게 수정
    baseline_df = pd.read_csv('retest5_fsr_log.csv').dropna()
    p_sum_baseline = baseline_df['fsr_left'] + baseline_df['fsr_right']
    P_NORMAL = p_sum_baseline.mean()
    SIGMA = max(p_sum_baseline.std(), 100.0)

    print(f"--- 분석 기준 설정 ---")
    print(f"Normal P_sum: {P_NORMAL:.1f}, Sigma: {SIGMA:.1f}\n")

    # 2. 분석 대상 파일 (2는 스펀지, 3은 포트홀 구간)
    files = {
        'Sponge': ['r2_1_fsr_log.csv', 'r2_2_fsr_log.csv'],
        'Pothole': ['r3_1_fsr_log.csv', 'r3_2_fsr_log.csv', 'r3_3_fsr_log.csv']
    }

    results = []
    for label, file_list in files.items():
        for f in file_list:
            if not os.path.exists(f): continue
            df = pd.read_csv(f).dropna()
            df['p_sum'] = df['fsr_left'] + df['fsr_right']
            df['z_score'] = (df['p_sum'] - P_NORMAL) / SIGMA
            
            # 판정
            df['status'] = 'Normal'
            df.loc[df['z_score'] < -2.5, 'status'] = 'Caution'
            df.loc[df['z_score'] < -5.5, 'status'] = 'Danger'
            
            counts = df['status'].value_counts()
            print(f"[{f}] ({label})")
            print(f" - Normal : {counts.get('Normal', 0)}")
            print(f" - Caution: {counts.get('Caution', 0)}")
            print(f" - Danger : {counts.get('Danger', 0)}\n")

if __name__ == "__main__":
    analyze_new_data()