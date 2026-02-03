import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# 1. 기본 설정
st.set_page_config(page_title="통합 설비 검침 시스템", layout="wide")

# CSS: 인쇄 시 불필요한 요소 제거 및 다크모드 배경 최적화
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    body, [data-testid="stAppViewContainer"] { background-color: #525659 !important; }
    [data-testid="stSidebar"] { background-color: #262730 !important; color: white; }
    @media print { .no-print { display: none !important; } .print-area { margin: 0; padding: 0; } }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "usage_data.csv"

# --- [공통 로직] 데이터 저장 및 로드 ---
def save_data(date, category, data_dict):
    new_rows = [{"검침일자": date, "구분": category, "항목": k, "수치": v} for k, v in data_dict.items()]
    new_df = pd.DataFrame(new_rows)
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = new_df
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    st.success(f"✅ {category} 데이터 저장 완료!")

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["검침일자", "구분", "항목", "수치"])

# --- [화면 1] 전기실 계량기 ---
def show_meter_page(date_str):
    st.header("⚡ 전기실 계량기 검침")
    data_list = [("39층", "HV39-1", 3000), ("10층(CGV)", "LV-1", 2400), ("10층(극장)", "LV-2", 800)]
    
    with st.expander("📝 지침 입력", expanded=True):
        inputs = {}
        cols = st.columns(3)
        for i, (loc, name, mul) in enumerate(data_list):
            inputs[name] = cols[i % 3].number_input(f"{name} ({loc})", key=f"m_{name}", step=0.1)
    
    if st.button("💾 서버 저장"):
        save_data(date_str, "계량기", inputs)

    # HTML 출력 양식 (간략화 예시)
    rows = "".join([f"<tr><td>{l}</td><td>{n}</td><td>{inputs[n]}</td><td>{m}</td></tr>" for l, n, m in data_list])
    html = f"<div style='background:white; padding:20px; color:black;'><h3>계량기 검침표 ({date_str})</h3><table border='1' style='width:100%; border-collapse:collapse; text-align:center;'><tr><th>위치</th><th>판넬</th><th>지침</th><th>배율</th></tr>{rows}</table><button onclick='window.print()' style='margin-top:10px;'>🖨️ 인쇄</button></div>"
    components.html(html, height=300)

# --- [화면 2] MOF 검침 ---
def show_mof_page(date_str):
    st.header("🏢 MOF 검침")
    mof_items = ["유효전력(중간)", "유효전력(최대)", "유효전력(경)", "무효전력(지상)", "최대수요전력"]
    
    with st.expander("📝 MOF 지침 입력", expanded=True):
        inputs = {item: st.number_input(item, key=f"mof_{item}") for item in mof_items}
    
    if st.button("💾 MOF 저장"):
        save_data(date_str, "MOF", inputs)

# --- [화면 3] 자고객 검침 ---
def show_second_meter_page(date_str):
    st.header("📊 자고객 검침 (전기차/소방)")
    customers = ["전기차A(B4F)", "전기차B(B4F)", "소방서(PH5)"]
    
    with st.expander("📝 자고객 지침 입력", expanded=True):
        inputs = {c: st.number_input(f"{c} 당월지침", key=f"sec_{c}") for c in customers}
        
    if st.button("💾 자고객 저장"):
        save_data(date_str, "자고객", inputs)

# --- [화면 4] 인버터 운전일지 ---
def show_inverter_page(date_str):
    st.header("🔄 인버터 운전일지")
    inv_list = ["인버터 #1", "인버터 #2", "인버터 #3"]
    
    with st.expander("📝 운전 데이터 입력", expanded=True):
        inputs = {}
        for inv in inv_list:
            c1, c2 = st.columns(2)
            inputs[f"{inv}_주파수"] = c1.number_input(f"{inv} 주파수(Hz)", key=f"hz_{inv}")
            inputs[f"{inv}_전류"] = c2.number_input(f"{inv} 전류(A)", key=f"a_{inv}")
            
    if st.button("💾 인버터 저장"):
        save_data(date_str, "인버터", inputs)

# --- [화면 5] 데이터 조회 및 분석 ---
def show_analysis_page():
    st.header("📋 데이터베이스 조회 및 시각화")
    df = load_data()
    
    if not df.empty:
        tab1, tab2 = st.tabs(["📑 테이블 조회", "📈 추이 분석"])
        with tab1:
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 엑셀(CSV) 다운로드", df.to_csv(index=False).encode('utf-8-sig'), "data_backup.csv")
            
            if st.button("🗑️ 전체 데이터 초기화", type="secondary"):
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
                    st.rerun()
        
        with tab2:
            target = st.selectbox("분석할 항목 선택", df["항목"].unique())
            chart_data = df[df["항목"] == target].sort_values("검침일자")
            st.line_chart(chart_data.set_index("검침일자")["수치"])
    else:
        st.info("저장된 데이터가 없습니다.")

# --- 메인 실행부 ---
def main():
    with st.sidebar:
        st.title("🔌 통합 관리 v1.0")
        menu = ["계량기 검침", "MOF 검침", "자고객 검침", "인버터 운전일지", "📊 데이터 분석/조회"]
        choice = st.radio("메뉴 이동", menu)
        date_str = st.date_input("날짜 선택", datetime.now()).strftime('%Y-%m-%d')
        st.info(f"선택일: {date_str}")

    if choice == "계량기 검침": show_meter_page(date_str)
    elif choice == "MOF 검침": show_mof_page(date_str)
    elif choice == "자고객 검침": show_second_meter_page(date_str)
    elif choice == "인버터 운전일지": show_inverter_page(date_str)
    elif choice == "📊 데이터 분석/조회": show_analysis_page()

if __name__ == "__main__":
    main()
