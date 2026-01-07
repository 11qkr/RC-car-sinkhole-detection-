RC카 싱크홀 탐지 FSR 파트

가상환경 FSR 활성화 -> 필요한 것 설치

arduino_sketch.ino : timestamp + fsr 센서값 측정
pc_logging_script.py : 데이터 수집을 위한 파일
realtime_detector.py : 파일 저장x 터미널에서 실시간 위험도 탐지
realtime_detector_final.py : 실시간 탐지 + AI/자율주행 연동을 위한 json 파일 생성

사용한 데이터 파일 
retest5_fst_log.csv : 정상 구간 주행 데이터
r2_1~3 : 스펀지 구간 주행 데이터
r3_1~3 : 지점토 포트홀 구간 주행 데이터
그 외 csv 파일은 최종 코드 구현에 사용하지 않음
