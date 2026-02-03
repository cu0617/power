import streamlit as st
import pandas as pd
import os
from datetime import datetime

# sidebar.py에 작성했던 저장 함수를 가져옵니다.
# 만약 파일이 분리되어 있다면 직접 정의해도 됩니다.
DB_FILE = "usage_data.csv"

def save_to_csv(date, category, data_dict):
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
    else:
        df = pd.DataFrame()
    
    new_data = {"검침일자": date, "구분": category}
    new_data.update(data_dict)
    
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def show_electricity_meter(date_str):
    st.subheader("⚡ 전기실 계량기 검침표")

    # 1. 데이터 정의
    data = [
        ("39층", "HV39-1", 3000), ("10층(CGV)", "LV-1", 2400), ("10층(극장)", "LV-2", 800),
        # ... (중략: 기존 데이터 리스트 그대로 사용)
    ]

    # 2. 데이터 입력 섹션 (Streamlit 위젯 사용)
    # HTML 입력창 대신 파이썬 위젯을 써야 "저장"이 가능합니다.
    st.info("💡 아래 표에 당월 지침을 입력한 후 하단의 [데이터 서버 저장] 버튼을 눌러주세요.")
    
    # 입력값을 담을 딕셔너리
    input_values = {}
    
    # 화면을 2열로 나누어 입력창 배치 (디자인 최적화)
    cols = st.columns(2)
    for i, (loc, panel, factor) in enumerate(data):
        col_idx = 0 if i < len(data)//2 else 1
        with cols[col_idx]:
            # 판넬별 입력창 생성
            val = st.number_input(f"{panel} ({loc})", min_value=0.0, step=0.1, key=f"inp_{panel}")
            input_values[panel] = val

    # 3. 저장 버튼
    if st.button("💾 데이터 서버 저장 (CSV)"):
        save_to_csv(date_str, "계량기 검침", input_values)
        st.success(f"{date_str} 데이터가 성공적으로 서버에 기록되었습니다!")
        st.balloons()

    st.markdown("---")
    
    # 4. 출력/인쇄용 화면 (기존 HTML 코드 활용)
    # 입력된 값을 HTML 표 안에 시각적으로 보여주기만 함
    if st.checkbox("🖨️ 인쇄용 화면 보기"):
        # 기존에 만드신 HTML 테이블 생성 로직을 여기에 넣어서 
        # 사용자가 입력한 input_values를 반영해 "보기 전용"으로 띄워줍니다.
        st.write("인쇄용 레이아웃이 여기에 표시됩니다.")
