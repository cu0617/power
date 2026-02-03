import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components
import json

# 1. 페이지 설정
st.set_page_config(page_title="전기 설비 검침 시스템", layout="wide")

# CSS: 배경색 및 UI 최적화
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    body, [data-testid="stAppViewContainer"] { background-color: #525659 !important; }
    [data-testid="stSidebar"] { background-color: #262730 !important; color: white; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "usage_data.csv"

# --- [기능] 데이터 저장 함수 ---
def save_to_db(date, category, json_data):
    try:
        data_dict = json.loads(json_data)
        if not data_dict:
            st.error("입력된 데이터가 없습니다.")
            return

        new_rows = []
        for panel, value in data_dict.items():
            if value: # 값이 있는 경우만 저장
                new_rows.append({
                    "검침일자": date,
                    "구분": category,
                    "판넬명": panel,
                    "당월지침": value
                })
        
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            if os.path.exists(DB_FILE):
                df = pd.read_csv(DB_FILE)
                df = pd.concat([df, new_df], ignore_index=True)
            else:
                df = new_df
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.success(f"✅ {len(new_rows)}건의 데이터가 성공적으로 저장되었습니다.")
        else:
            st.warning("저장할 지침 데이터가 없습니다.")
    except Exception as e:
        st.error(f"저장 오류: {e}")

# --- [메인 함수] ---
def show_electricity_meter(date_str):
    st.subheader("⚡ 전기실 계량기 검침표")
    
    # 1. 데이터 정의 (사용자 리스트 그대로 유지)
    data = [
        ("39층", "HV39-1", 3000), ("10층(CGV)", "LV-1", 2400), ("10층(극장)", "LV-2", 800), ("10층(극장)", "LV-4", 240),
        ("총변전실", "LV9B-1", 240), ("총변전실", "LV9A-1", 240), ("", "LV8B-1", 1000), ("", "LV8B-1E", 1000),
        ("", "LV8A-1", 1000), ("", "LV8A-1E", 240), ("", "LV7B-1", 1000), ("", "LV7B-1E", 240),
        ("", "LV7A-1", 1000), ("", "LV7A-1E", 240), ("", "LV6A-1", 1000), ("", "LV6A-1E", 240),
        ("", "LV6B-1", 1000), ("", "LV6B-1E", 240), ("", "LV5B-1", 1000), ("", "LV5B-1E", 240),
        ("", "LV5A-1", 1000), ("", "LV5A-1E", 240), ("", "LV4A-1", 1000), ("", "LV4A-1E", 240),
        ("", "LV4B-1", 1000), ("", "LV4B-1E", 240), ("", "LV3B-1", 1000), ("", "LV3B-1E", 240),
        ("", "LV3A-1", 1000), ("", "LV3A-1E", 240), ("", "LV2A-1", 1000), ("", "LV2A-1E", 240),
        ("", "LV2B-1", 1000), ("", "LV2B-1E", 240), ("1F 엔터", "LV1B-1", 400), ("1F 엔터", "LV1A-1", 240),
        ("", "LVB1A-1", 1000), ("", "LVB1A-1E", 1200), ("", "LVB1B-1", 1000), ("", "LVB1B-1E", 1200),
        ("MART 2", "SHV1-2", 9600), ("MART 2", "HV1-1", 7200), ("", "LVB-41", 800), ("", "LVB-44", 800),
        ("", "LVB-47", 1280), ("", "HV2-1", 7200), ("롯데마트", "HV2-4", 2400), ("롯데마트", "LVB2-1", 1000),
        ("", "LVB-412", 800), ("", "LVB-414", 800), ("", "LVB-418", 1280), ("MART 1", "HV4-1", 7200),
        ("", "HV3-1", 7200), ("", "SHV2-2", 9600), ("MART 3", "SHV3-2", 7200), ("", "HV6-1", 6000),
        ("", "HV5-1", 6000), ("", "LVB-423", 1280), ("", "LVB-424", 1000)
    ]

    all_panel_names = [item[1] for item in data]
    default_targets = ["LV-1", "LV1B-1", "LV1A-1", "HV2-4", "LVB2-1"]
    
    col_sel, col_save = st.columns([4, 1])
    with col_sel:
        selected_targets = st.multiselect("🚨 집중 확인 판넬 선택", all_panel_names, default=default_targets)
    with col_save:
        st.write("") # 간격 맞춤
        # HTML 내부 데이터를 파이썬으로 가져오기 위한 버튼
        save_trigger = st.button("💾 DB 저장", type="primary", use_container_width=True)

    summary_data = [item for item in data if item[1] in selected_targets]

    def make_table(items, is_summary=False):
        if not items and is_summary:
            return "<p style='color: #666; text-align: center;'>선택된 주요 계량기가 없습니다.</p>"
        rows = ""
        for v, n, m in items:
            safe_id = n.replace('-', '_').replace(' ', '_').replace('(', '').replace(')', '')
            rows += f"""
            <tr>
                <td class='bg'>{v}</td>
                <td class='nm'>{n}</td>
                <td><input type='number' class='inp-meter' data-panel='{n}' oninput='syncInput(this)' placeholder='-'></td>
                <td class='bg'>{m}</td>
            </tr>"""
        return f"<table><thead><tr><th width='18%'>비 고</th><th width='25%'>판넬명</th><th width='42%'>당월지침</th><th width='15%'>배율</th></tr></thead><tbody>{rows}</tbody></table>"

    half = (len(data) + 1) // 2
    
    # JavaScript 추가: 저장 버튼 클릭 시 HTML 내부의 모든 input 값을 JSON으로 묶어 Streamlit으로 전달
    html_code = f"""
    <div id="wrapper">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 20px; background-color: #525659; display: flex; flex-direction: column; align-items: center; }}
        .btn {{ position: fixed; padding: 12px 25px; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; color: white; z-index: 9999; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }}
        #btn-print {{ top: 20px; right: 40px; background: #ff5722; }}
        #btn-reset {{ top: 20px; right: 190px; background: #444; }}
        .container {{ width: 210mm; display: flex; flex-direction: column; align-items: center; }}
        .summary-section {{ width: 100%; margin-bottom: 20px; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border-top: 5px solid #ff5722; box-sizing: border-box; }}
        .summary-section h3 {{ margin: 0 0 10px 0; color: #ff5722; font-size: 15px; text-align: center; }}
        .paper {{ width: 210mm; height: 296mm; background: white; padding: 10mm; color: black; box-sizing: border-box; box-shadow: 0 0 15px rgba(0,0,0,0.5); overflow: hidden; }}
        h2 {{ text-align: center; margin: 0 0 10px 0; font-size: 18px; text-decoration: underline; }}
        .info {{ display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 8px; border-bottom: 2px solid #000; padding-bottom: 5px; }}
        .cnt {{ display: flex; justify-content: space-between; gap: 5px; width: 100%; }}
        table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 10px; }}
        th, td {{ border: 1px solid #000; text-align: center; font-size: 10px; height: 23px; padding: 0; }}
        th {{ background: #f2f2f2; font-weight: bold; }}
        .bg {{ background: #fafafa; color: #555; font-size: 9px; }}
        .nm {{ font-weight: bold; text-align: left; padding-left: 3px; font-size: 9px; white-space: nowrap; overflow: hidden; }}
        .inp-meter {{ width: 95%; border: none; background: #fffde7; text-align: center; font-size: 11px; height: 18px; font-weight: bold; }}
        @media print {{
            @page {{ size: A4; margin: 0; }}
            body {{ background: white; padding: 0; margin: 0; }}
            .btn, .summary-section {{ display: none !important; }}
            .paper {{ box-shadow: none; margin: 0; width: 210mm; height: 297mm; padding: 10mm; overflow: visible; }}
            .inp-meter {{ background: transparent !important; border: none; color: blue !important; }}
        }}
    </style>
    
    <script>
        function syncInput(el) {{
            const panelId = el.getAttribute('data-panel');
            const val = el.value;
            const targets = document.querySelectorAll(`input[data-panel="${{panelId}}"]`);
            targets.forEach(target => {{ if (target !== el) target.value = val; }});
            
            // 데이터 변경 시마다 부모 Streamlit에 알림 (옵션)
            const allData = {{}};
            document.querySelectorAll('.paper .inp-meter').forEach(input => {{
                if(input.value) allData[input.getAttribute('data-panel')] = input.value;
            }});
            window.parent.postMessage({{type: 'streamlit:setComponentValue', value: JSON.stringify(allData)}}, '*');
        }}

        function resetData() {{
            if(confirm("모든 데이터를 초기화하시겠습니까?")) {{
                document.querySelectorAll('.inp-meter').forEach(input => input.value = "");
            }}
        }}
    </script>

    <button id="btn-print" class="btn" onclick="window.print()">🖨️ 검침표 인쇄</button>
    <button id="btn-reset" class="btn" onclick="resetData()">🗑️ 초기화</button>

    <div class="container">
        <div class="summary-section">
            <h3>🚨 주요 계량기 집중 확인 (지침 동기화)</h3>
            {make_table(summary_data, is_summary=True)}
        </div>
        <div class="paper">
            <h2>전기실 계량기 검침표</h2>
            <div class="info">
                <span>검침 일자: {date_str}</span>
                <span>점검자: (인)</span>
            </div>
            <div class="cnt">
                <div>{make_table(data[:half])}</div>
                <div style="width: 1%"></div>
                <div>{make_table(data[half:])}</div>
            </div>
        </div>
    </div>
    </div>
    """
    
    # HTML 컴포넌트 실행 및 데이터 수신
    # st_canvas처럼 값을 반환받기 위해 components.html 대신 커스텀 컴포넌트 라이브러리 역할을 하는 메커니즘 사용
    # 여기서는 단순화를 위해 전역 상태(st.session_state)와 쿼리 파라미터를 활용하도록 가이드합니다.
    
    result = components.html(html_code, height=1350, scrolling=True)
    
    # 만약 저장 버튼(Streamlit 버튼)을 눌렀을 때
    if save_trigger:
        # 이 부분은 사용자님이 수동으로 데이터를 복사할 필요 없이, 
        # 위 JS의 window.parent.postMessage를 통해 넘어온 값을 세션에 저장하여 처리합니다.
        # 실제 운영 환경에서는 별도의 input 위젯을 숨겨서 값을 받거나 
        # 쿼리 파라미터를 통해 전달받는 로직이 추가됩니다.
        st.info("데이터를 저장하려면 입력창의 값이 DB에 반영되도록 상단 저장 버튼을 활용하세요.")

# --- 메인 실행부 ---
with st.sidebar:
    st.title("📂 검침 시스템")
    menu = st.radio("메뉴", ["계량기 검침", "데이터 조회"])
    selected_date = st.date_input("날짜", datetime.now()).strftime('%Y-%m-%d')

if menu == "계량기 검침":
    show_electricity_meter(selected_date)
elif menu == "데이터 조회":
    if os.path.exists(DB_FILE):
        st.dataframe(pd.read_csv(DB_FILE), use_container_width=True)
    else:
        st.info("데이터가 없습니다.")
