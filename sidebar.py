import streamlit as st
from datetime import datetime

# 1. 페이지 설정 및 배경 최적화
st.set_page_config(page_title="전기 설비 검침 시스템", layout="centered")

# 배경색 및 UI 숨기기 CSS
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 0px;}
    body, [data-testid="stAppViewContainer"] { background-color: #525659 !important; }
    [data-testid="stSidebar"] { background-color: #262730 !important; color: white; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # 2. 사이드바 구성
    with st.sidebar:
        st.title("📂 검침 시스템")
        st.subheader("메뉴 선택")
        
        # 메뉴 리스트 및 파일 매핑 (쉼표 추가됨)
        menu_options = {
            "계량기 검침": "electricity_meter",
            "MOF 검침": "mof",           # <- 여기 끝에 쉼표가 꼭 있어야 합니다.
            "자고객 검침": "second_meter",
            "인버터 운전일지": "inverter"
        }
        choice = st.radio("검침표 종류를 선택하세요", list(menu_options.keys()))
        
        st.markdown("---")
        
        # 공통 날짜 선택
        selected_date = st.date_input("🗓️ 검침 일자 선택", datetime.now())
        date_str = selected_date.strftime('%Y-%m-%d')
        
        st.info("💡 인쇄 시 브라우저 설정에서 '배경 그래픽'을 체크해 주세요.")

    # 3. 메뉴 선택에 따른 외부 모듈 로드
    if choice == "계량기 검침":
        try:
            from electricity_meter import show_electricity_meter
            show_electricity_meter(date_str)
        except ImportError:
            st.warning("`electricity_meter.py` 파일을 찾을 수 없습니다.")

    elif choice == "MOF 검침":
        try:
            from mof import show_mof_detail
            show_mof_detail(date_str)
        except ImportError:
            st.warning("`mof.py` 파일을 찾을 수 없습니다.")

    elif choice == "자고객 검침":
        try:
            # 들여쓰기 교정 완료
            from second_meter import show_second_meter
            show_second_meter(date_str)
        except ImportError:
            st.warning("`second_meter.py` 파일을 찾을 수 없습니다.")        

    elif choice == "인버터 운전일지":
        try:
            from inverter import show_inverter_log
            show_inverter_log(date_str)
        except ImportError:
            st.warning("`inverter.py` 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()

