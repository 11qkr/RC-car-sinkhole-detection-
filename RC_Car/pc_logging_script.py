import serial
import time

ARDUINO_PORT = 'COM6' # 본인 포트에 맞게 수정
BAUD_RATE = 115200 
CSV_FILE = 'r3_3_fsr_log.csv'

try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) 

    print(f"Logging data to {CSV_FILE}... Press Ctrl+C to stop.")

    with open(CSV_FILE, 'w', encoding='utf-8') as f:
        f.write("timestamp,fsr_left,fsr_right\n")
        
        while True:
            line = ser.readline().decode('utf-8').strip()
            
            if line:
                # 만약 읽어온 줄에 "timestamp"가 포함되어 있다면 (중복 헤더 방지)
                if "timestamp" in line:
                    continue 
                
                # 순수 데이터만 파일에 기록
                f.write(line + '\n')
                print(f"Recording: {line}") # 실시간 데이터 확인용

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")