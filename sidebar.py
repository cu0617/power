import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 설정 및 배경 최적화
st.set_page_config(page_title="전기 설비 검침 시스템", layout="centered")

# 배경색 및 UI 숨기기 CSS
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 20px;}
    body, [data-testid="stAppViewContainer"] { background-color: #525659 !important; }
    [data-testid="stSidebar"] { background-color: #262730 !important; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터베이스(파일) 관련 함수 ---
DB_FILE = "usage_data.csv"

def save_to_csv(date, category, data_dict):
    """입력된 딕셔너리 데이터를 CSV 파일에 저장하는 함수"""
    # 기존 데이터 로드
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
    else:
        df = pd.DataFrame()

    # 신규 데이터 정리
    new_data = {"검침일자": date, "구분": category}
    new_data.update(data_dict) # 상세 검침값 추가
    
    new_df = pd.DataFrame([new_data])
    
    # 데이터 합치기 및 저장
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    st.success(f"✅ {date} {category} 기록이 안전하게 서버 파일로 저장되었습니다!")

def main():
    # 2. 사이드바 구성
    with st.sidebar:
        st.title("📂 검침 시스템")
        st.subheader("메뉴 선택")
        
        menu_options = {
            "계량기 검침": "electricity_meter",
            "MOF 검침": "mof",
            "자고객 검침": "second_meter",
            "인버터 운전일지": "inverter",
            "📊 데이터 조회/다운로드": "view_db"  # DB 관리 메뉴 추가
        }
        choice = st.radio("메뉴를 선택하세요", list(menu_options.keys()))
        
        st.markdown("---")
        
        # 공통 날짜 선택
        selected_date = st.date_input("🗓️ 검침 일자 선택", datetime.now())
        date_str = selected_date.strftime('%Y-%m-%d')
        
        st.info("💡 인쇄 시 브라우저 설정에서 '배경 그래픽'을 체크해 주세요.")

    # 3. 메뉴 선택에 따른 화면 표시
    if choice == "📊 데이터 조회/다운로드":
        st.title("📋 누적 검침 데이터베이스")
        if os.path.exists(DB_FILE):
            view_df = pd.read_csv(DB_FILE)
            st.dataframe(view_df, use_container_width=True)
            
            # 엑셀 다운로드 기능
            csv = view_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 전체 데이터 엑셀(CSV) 다운로드",
                data=csv,
                file_name=f"전기검침기록_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            if st.button("🗑️ 임시: 최신 기록 한 줄 삭제"):
                 df = pd.read_csv(DB_FILE)
                 df[:-1].to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                 st.rerun()
        else:
            st.info("아직 저장된 데이터가 없습니다. 검침을 진행해 주세요.")

    else:
        # 각 검침 페이지 로드
        if choice == "계량기 검침":
            try:
                from electricity_meter import show_electricity_meter
                # 데이터를 반환받을 수 있도록 구조를 살짝 변경할 수 있습니다.
                show_electricity_meter(date_str)
            except ImportError: st.warning("파일을 찾을 수 없습니다.")

        elif choice == "MOF 검침":
            try:
                from mof import show_mof_detail
                show_mof_detail(date_str)
            except ImportError: st.warning("파일을 찾을 수 없습니다.")

        # ... (자고객, 인버터 동일 구조)

if __name__ == "__main__":
    main()
