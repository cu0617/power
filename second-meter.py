import streamlit as st
import streamlit.components.v1 as components

def show_second_meter(date_str):
    st.subheader("📊 자고객 계량기 검침표")

    # 1. 세션 상태 초기화 (유령 문자 제거 완료)
    if 'ev_sections' not in st.session_state:
        default_items = [
            ["4", "전월수전유효전력량(kwh) 중간부하", "KWH"],
            ["5", "전월수전유효전력량(kwh) 최대부하", "KWH"],
            ["6", "전월수전유효전력량(kwh) 경부하", "KWH"],
            ["7", "전월수전(지상) 무효전력량 (중간부하)", "KVARH"],
            ["8", "전월수전(지상) 무효전력량 (최대부하)", "KVARH"],
            ["9", "전월수전(지상) 무효전력량 (경부하)", "KWH"],
            ["10", "전월수전 최대수요전력(중간부하)", "KWH"],
            ["11", "전월수전 최대수요전력(최대부하)", "KWH"]
        ]
        
        st.session_state.ev_sections = [
            {
                "title": "전력검침량 (B4F, 전기자동차A)",
                "sub": "(배율 : *1)",
                "meter": "01-5341-6416",
                "items": [item[:] for item in default_items]
            },
            {
                "title": "전력검침량 (B4F, 전기자동차B)",
                "sub": "(배율 : *100)",
                "meter": "01-5883-9432",
                "items": [item[:] for item in default_items]
            },
            {
                "title": "전력검침량 (PH5, 소방서)",
                "sub": "(배율 : *1)",
                "meter": "01-3537-4137",
                "items": [item[:] for item in default_items]
            }
        ]

    # --- [HTML 내용 생성 함수 수정] ---
    def generate_html_content():
        content = ""
        total = len(st.session_state.ev_sections)
        for idx, sec in enumerate(st.session_state.ev_sections):
            # [핵심 수정]: <td></td> 빈칸 대신 <input> 태그 삽입
            rows = "".join([f"<tr><td>{i[0]}</td><td class='left'>{i[1]}</td><td>{i[2]}</td><td><input type='text' class='inp-val' placeholder='-'></td></tr>" for i in sec['items']])
            page_break_class = "page-break" if (idx + 1) % 3 == 0 and (idx + 1) != total else ""
            
            content += f"""
            <div class='section-container {page_break_class}'>
                <div class='section-header'>
                    <div>{sec['title']}<br><small>{sec['sub']}</small></div>
                    <div class='meter-no'>계량기 번호<br>({sec['meter']})</div>
                </div>
                <table>
                    <thead><tr><th width='10%'>순번</th><th width='55%'>내용</th><th width='14%'>단위</th><th width='20%'>당월지침</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
            """
        return content

    html_template = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 10px 0; background: #525659; display: flex; flex-direction: column; align-items: center; }}
        .paper {{ width: 200mm; margin: 0 auto; background: white; padding: 15mm; color: black; box-sizing: border-box; box-shadow: 0 0 15px rgba(0,0,0,0.5); }}
        h2 {{ text-align: center; margin: 0 0 20px 0; font-size: 24px; text-decoration: underline; }}
        .info {{ display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 15px; font-weight: bold; border-bottom: 2px solid #000; padding-bottom: 5px; }}
        
        .section-container {{ margin-bottom: 15px; }}
        .section-header {{ display: flex; justify-content: space-between; align-items: center; background: #fdfaf0; border: 1px solid #000; border-bottom: none; padding: 8px 15px; font-size: 12px; font-weight: bold; text-align: center; }}
        .meter-no {{ border-left: 1px solid #000; padding-left: 15px; width: 120px; }}
        
        table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 5px; }}
        th, td {{ border: 1px solid #000; text-align: center; font-size: 11px; height: 23px; }}
        th {{ background: #f2f2f2; }}
        .left {{ text-align: left; padding-left: 10px; }}

        /* [입력창 스타일 추가] */
        .inp-name {{ border: none; border-bottom: 1px dotted #000; width: 100px; text-align: center; background: #fffde7; font-weight: bold; font-family: inherit; }}
        .inp-val {{ width: 90%; border: none; background: #fffde7; text-align: center; font-size: 12px; font-weight: bold; color: blue; }}
        .inp-val:focus {{ background: #fff; outline: 1px solid #FF9800; }}

        /* 버튼 설정 */
        .btn {{ position: fixed; padding: 12px 25px; color: white; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; z-index: 100; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
        #btn-save {{ position: absolute; top: 20px; right: 130px; background: #28A745; }}
        #btn-print {{ top: 20px; right: 20px; background: #FF9800; }}
        #btn-reset {{ top: 20px; left: 20px; background: #444; }}

        @media print {{
            body {{ background: white; padding: 0; margin: 0; }}
            .btn {{ display: none !important; }}
            .paper {{ box-shadow: none; padding: 10mm; width: 210mm; margin: 0; }}
            .inp-val, .inp-name {{ background: transparent !important; border: none; color: blue !important; }}
            .page-break {{ page-break-after: always; }}
        }}
    </style>

    <script>
        function resetValues() {{
            if(confirm("입력된 모든 지침과 성명을 초기화하시겠습니까?")) {{
                document.querySelectorAll('.inp-val, .inp-name').forEach(el => el.value = "");
            }}
        }}
    </script>
    <button id="btn-save" class="btn" onclick="saveData()">💾 저장</button>
    <button id="btn-print" class="btn" onclick="window.print()">🖨️ 인쇄</button>
    <button id="btn-reset" class="btn" onclick="resetValues()">🗑️ 데이터 초기화</button>

    <div class="paper">
        <h2>자고객 계량기 검침표</h2>
        <div class="info">
            <span>검침 일자: {date_str}</span>
            <span>점검자: <input type="text" class="inp-name" placeholder="          "> (인)</span>
        </div>
        {generate_html_content()}
    </div>
    """
    
    dynamic_height = max(800, len(st.session_state.ev_sections) * 450)
    components.html(html_template, height=dynamic_height, scrolling=True)

    # --- 하단 관리 탭 (항목 수정 등) ---
    st.divider()
    tab1, tab2 = st.tabs(["✏️ 항목 및 고객 정보 수정", "⚙️ 고객 추가/삭제"])
    # ... (기존 탭 로직 유지)

    with tab1:
        if st.session_state.ev_sections:
            titles = [f"{i+1}. {s['title']} ({s['meter']})" for i, s in enumerate(st.session_state.ev_sections)]
            sel = st.selectbox("수정할 고객 선택", range(len(titles)), format_func=lambda x: titles[x])
            sec = st.session_state.ev_sections[sel]
            with st.container(border=True):
                c = st.columns([2, 1, 1])
                sec['title'] = c[0].text_input("고객명", sec['title'], key=f"edit_t{sel}")
                sec['sub'] = c[1].text_input("배율", sec['sub'], key=f"edit_s{sel}")
                sec['meter'] = c[2].text_input("계량기번호", sec['meter'], key=f"edit_m{sel}")
                
                st.write("**상세 항목 편집**")
                new_items = []
                for i_idx, item in enumerate(sec['items']):
                    ic = st.columns([1, 4, 2, 1])
                    r_no = ic[0].text_input("N", item[0], key=f"n{sel}{i_idx}", label_visibility="collapsed")
                    r_tx = ic[1].text_input("T", item[1], key=f"x{sel}{i_idx}", label_visibility="collapsed")
                    r_ut = ic[2].text_input("U", item[2], key=f"u{sel}{i_idx}", label_visibility="collapsed")
                    if not ic[3].button("❌", key=f"del_row_{sel}_{i_idx}"):
                        new_items.append([r_no, r_tx, r_ut])
                
                sec['items'] = new_items
                if st.button("➕ 항목 추가", key=f"add_row_btn_{sel}"):
                    sec['items'].append(["", "", "KWH"])
                    st.rerun()
        else:
            st.warning("등록된 고객이 없습니다.")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            with st.form("new_customer_form", clear_on_submit=True):
                st.write("**🆕 새로운 고객 추가**")
                nt = st.text_input("고객명/장소")
                nm = st.text_input("계량기 번호")
                ns = st.text_input("배율", value="(배율 : *1)")
                if st.form_submit_button("➕ 리스트에 추가"):
                    if nt:
                        st.session_state.ev_sections.append({
                            "title": nt, "sub": ns, "meter": nm if nm else "00-00-00",
                            "items": [
                                ["4", "전월수전유효전력량(kwh) 중간부하", "KWH"],
                                ["5", "전월수전유효전력량(kwh) 최대부하", "KWH"],
                                ["6", "전월수전유효전력량(kwh) 경부하", "KWH"],
                                ["7", "전월수전(지상) 무효전력량 (중간부하)", "KVARH"],
                                ["8", "전월수전(지상) 무효전력량 (최대부하)", "KVARH"],
                                ["9", "전월수전(지상) 무효전력량 (경부하)", "KWH"],
                                ["10", "전월수전 최대수요전력(중간부하)", "KWH"],
                                ["11", "전월수전 최대수요전력(최대부하)", "KWH"]
                            ]
                        })
                        st.rerun()
        with col2:
            st.write("**🗑️ 고객 리스트 삭제**")
            if st.session_state.ev_sections:
                del_list = [f"{i+1}. {s['title']}" for i, s in enumerate(st.session_state.ev_sections)]
                target = st.selectbox("삭제할 고객 선택", range(len(del_list)), format_func=lambda x: del_list[x])
                if st.button("🔥 선택 고객 삭제", type="primary"):
                    st.session_state.ev_sections.pop(target)
                    st.rerun()
