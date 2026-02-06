import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- 1. 로컬 DB 연결 (파일로 저장됨) ---
conn = sqlite3.connect('meter_data.db', check_same_thread=False)
c = conn.cursor()

# 테이블 생성 (최초 1회)
c.execute('''CREATE TABLE IF NOT EXISTS readings 
             (date TEXT, meter_id TEXT, value REAL, cost REAL)''')
conn.commit()

# --- 2. 관리자 설정 로직 (코드 수정 없이 제어) ---
st.sidebar.title("⚙️ 관리자 설정")
unit_price = st.sidebar.number_input("현재 kWh당 단가(원)", value=125.0)
meter_list = ["본관 1층", "본관 2층", "별관 기계실"] # 이 리스트도 DB에서 불러오게 할 수 있음

# --- 3. 메인 화면: 검침 입력 ---
st.title("🔌 검침 데이터 관리 시스템")

tab1, tab2, tab3 = st.tabs(["데이터 입력", "통계 및 그래프", "외부 데이터 비교"])

with tab1:
    st.header("📝 수기 검침 수치 기입")
    with st.form("input_form"):
        date = st.date_input("검침 날짜", datetime.date.today())
        selected_meter = st.selectbox("계량기 선택", meter_list)
        reading_value = st.number_input("현재 지침 수치", min_value=0.0)
        
        if st.form_submit_button("데이터 저장"):
            # 사용량 계산 및 DB 저장 로직 (이전 값 불러오기 포함)
            calculated_cost = reading_value * unit_price
            c.execute("INSERT INTO readings VALUES (?, ?, ?, ?)", 
                      (date, selected_meter, reading_value, calculated_cost))
            conn.commit()
            st.success(f"{selected_meter} 데이터가 안전하게 저장되었습니다.")

# --- 4. 그래프 추출 (2단계에서 구현) ---
with tab2:
    st.header("📈 연도별/계량기별 분석")
    # DB에서 데이터를 Pandas로 읽어와 Plotly로 시각화
