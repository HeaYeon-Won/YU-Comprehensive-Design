# 졸업작품 주제

## 이동체의 포트홀 인식을 통한 포트홀 위치 정보 조회 시스템과 포트홀에서의 카메라/센서 수평 오차 저감 장치

- update
  - ver0(2021-01-04), 포트홀 인식 후 이미지와 gps 좌표를 server로 넘기고 포트홀에서 흔들림 발생 시 서보모터를 이용한 카메라/센서의 수평 유지
    + server에서 현재 1대1 socket 통신만 가능 -> 다중 connect가 되도록 수정 (이외의 네트워크 상태에 따른 기능 ack, timeout 등 고려)
    + 서보모터를 이용한 수평 유지 기능의 반응속도, 정확성 향상 필요 -> 실험을 통한 수정
    + 수평 유지 기능을 적용할 하드웨어 구현 필요

-이번주 해야할일
  -norql : 공부(사용방법, 코드에서 제어방법)
  -~~라즈베리파이 코드 빼와서 올리기(master, Server)~~
  -자료정리 및 공부 자료 올리기(상보필터)
