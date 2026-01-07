# 1주차 캘리브레이션 기능 구현 (Python)
# calibration_utils.py (예시 파일 이름)

import numpy as np

def calculate_offset(zero_load_readings):
    """
    무하중 상태(영점)에서의 센서 값 평균을 계산함.
    :param zero_load_readings: 리스트 형태의 무하중 센서 원본 값들 (예: [10, 12, 11, ...])
    :return: 무하중 센서 값의 평균 (offset)
    """
    if not zero_load_readings:
        return 0.0 # 데이터가 없으면 0 반환
    return np.mean(zero_load_readings)

def calculate_span(known_load_readings, known_load_grams, offset):
    """
    특정 무게를 올렸을 때의 센서 값과 오프셋을 기반으로 스팬(감도)을 계산함.
    :param known_load_readings: 특정 무게를 올렸을 때의 센서 원본 값들 (예: [300, 310, 295, ...])
    :param known_load_grams: 센서 위에 올린 알려진 무게 (그램 단위, 예: 1000g)
    :param offset: 이전에 계산된 영점 오프셋
    :return: 센서의 감도 (예: 1그램당 몇 analogRead 값 변화)
    """
    if not known_load_readings or known_load_grams <= 0:
        return 1.0 # 유효하지 않은 입력 시 기본값 반환
    
    # 순수하게 무게 때문에 변한 센서 값의 평균
    avg_reading_under_load = np.mean(known_load_readings)
    
    # (무게 올린 평균 - 영점) / 알려진 무게 = 1g당 센서 값 변화
    # 이 값을 'scale_factor' 또는 'span'이라 부를 수 있음
    span_value = (avg_reading_under_load - offset) / known_load_grams
    
    # span_value가 너무 작거나 0이면 문제가 있으므로 방지
    if span_value == 0:
        return 1.0 # 0이면 나눗셈 오류 방지
    
    return span_value

# 나중에 센서 값을 물리량(그램)으로 변환할 함수 (예시)
def convert_to_grams(raw_reading, offset, span):
    """
    원본 센서 값을 오프셋과 스팬을 이용해 물리량(그램)으로 변환함.
    :param raw_reading: 현재 센서 원본 값
    :param offset: 계산된 오프셋
    :param span: 계산된 스팬
    :return: 그램 단위의 무게
    """
    if span == 0: # 나눗셈 오류 방지
        return 0.0
    return (raw_reading - offset) / span

if __name__ == "__main__":
    # 이 부분은 1주차에 직접 실행하며 테스트해 볼 수 있는 예시임.
    # 실제 FSR 데이터가 아니지만, 함수 작동을 이해하는 데 도움 됨.

    # 1. 영점(무하중) 데이터 예시
    zero_data_left = [10, 12, 11, 13, 10]
    zero_data_right = [15, 14, 16, 15, 14]

    offset_left = calculate_offset(zero_data_left)
    offset_right = calculate_offset(zero_data_right)
    print(f"Left FSR Offset: {offset_left:.2f}")
    print(f"Right FSR Offset: {offset_right:.2f}")

    # 2. 스팬(알려진 무게 500g) 데이터 예시
    # (실제 2주차에 이 데이터를 FSR에 500g 올리고 얻게 됨)
    load_data_left = [210, 205, 215, 208, 212] # 500g 올렸을 때 값
    load_data_right = [230, 225, 235, 228, 232] # 500g 올렸을 때 값
    known_weight_grams = 500 # 올린 무게

    span_left = calculate_span(load_data_left, known_weight_grams, offset_left)
    span_right = calculate_span(load_data_right, known_weight_grams, offset_right)
    print(f"Left FSR Span (analog/gram): {span_left:.2f}")
    print(f"Right FSR Span (analog/gram): {span_right:.2f}")

    # 3. 변환 테스트 (예시)
    test_raw_left = 150 # 테스트용 raw 값
    test_raw_right = 180 # 테스트용 raw 값
    
    converted_grams_left = convert_to_grams(test_raw_left, offset_left, span_left)
    converted_grams_right = convert_to_grams(test_raw_right, offset_right, span_right)
    print(f"Test Left FSR ({test_raw_left} raw) -> {converted_grams_left:.2f} grams")
    print(f"Test Right FSR ({test_raw_right} raw) -> {converted_grams_right:.2f} grams")