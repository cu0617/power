import streamlit as st
import streamlit.components.v1 as components
import json

def show_inverter_log(date_str):
    st.subheader("📋 인버터 운전일지")

    if 'inv_locations' not in st.session_state:
        st.session_state.inv_locations = ["웨딩 3층", "웨딩 4층", "엔터식스"]
    
    # 1. 대량 입력 설정창
    with st.expander("🚀 데이터 대량 입력 및 관리 도구", expanded=False):
        col1, col2 = st.columns([2, 1])
        all_days = [str(i) for i in range(1, 32)]
        target_days = col1.multiselect("📅 날짜 선택", all_days)
        target_locs = col2.multiselect("📍 대상 장소", st.session_state.inv_locations, default=st.session_state.inv_locations)

        st.divider()
        
        c1, c2, c3 = st.columns([1.5, 1, 1])
        target_zones = c1.multiselect("🏢 대상 구역", ["A", "B", "C", "D"], default=["A", "B", "C", "D"])
        set_freq = c2.number_input("Hz (주파수)", value=60.0, step=0.1)
        set_hour = c3.number_input("Hour (시간)", value=0.0, step=0.5)
        
        b1, b2 = st.columns(2)
        if b1.button("⚡ 선택 조건 일괄 적용", use_container_width=True):
            st.session_state.bulk_command = {
                "type": "apply", "days": target_days, "locs": [l.replace(" ", "_") for l in target_locs],
                "zones": target_zones, "freq": set_freq, "hour": set_hour
            }
        if b2.button("🗑️ 화면 데이터 전체 초기화", use_container_width=True):
            st.session_state.bulk_command = {"type": "clear"}

    selected_locs = st.multiselect("현재 표시 장소", st.session_state.inv_locations, default=st.session_state.inv_locations)
    year_month = date_str[:7].replace("-", "년 ") + "월"

    def generate_location_html(loc_name):
        base_data = {"A": 64.3, "B": 66.25, "C": 57.81, "D": 64.3}
        zones = ["A", "B", "C", "D"]
        pages_html = ""
        # 31일까지 잘리지 않도록 6일씩 5페이지 분할 (6, 6, 6, 6, 7)
        page_breaks = [0, 6, 12, 18, 24, 31] 
        loc_id_safe = loc_name.replace(" ", "_")
        
        for idx in range(len(page_breaks) - 1):
            start_day = page_breaks[idx] + 1
            end_day = page_breaks[idx+1]
            rows_html = ""
            for day in range(start_day, end_day + 1):
                for i, zone in enumerate(zones):
                    day_td = f'<td rowspan="5" class="day-cell">{day}</td>' if i == 0 else ""
                    row_id = f"{loc_id_safe}_{day}_{zone}"
                    rows_html += f"""
                    <tr class="data-row">
                        {day_td}<td>{zone}</td>
                        <td id="base_{row_id}">{base_data[zone]}</td>
                        <td><input type="number" class="inp-freq" id="freq_{row_id}" step="0.1" oninput="calcRow('{row_id}')"></td>
                        <td><input type="number" class="inp-hour" id="hour_{row_id}" step="0.5" oninput="calcRow('{row_id}')"></td>
                        <td class="usage-res" id="usage_{row_id}">0.00</td>
                    </tr>"""
                rows_html += f"""<tr class="subtotal"><td colspan="4" style="font-weight:bold; background:#f9f9f9;">일 계</td><td class="day-total" id="total_{loc_id_safe}_{day}" style="font-weight:bold; color:red;">0.00</td></tr>"""
            
            is_first_page = (idx == 0)
            header = f"""
            <div class="header-box">
                <h2 class="title">{year_month} ({loc_name}) 인버터 운전일지</h2>
                <div class="info-row"><span>검침 일자: {date_str}</span><span>장소: {loc_name}</span></div>
            </div>
            """ if is_first_page else "<div class='header-spacer'></div>"
            
            # 각 페이지 마지막 줄 바꿈 제어
            pages_html += f'<div class="paper">{header}<table><thead><tr><th width="10%">일자</th><th width="10%">구역</th><th>실측(KW)</th><th>주파수(HZ)</th><th>시간(H)</th><th>사용량(KW)</th></tr></thead><tbody>{rows_html}</tbody></table></div>'
        return pages_html

    summary_rows = "".join([f"<tr><td style='background:#f2f2f2; width:50%;'>{loc}</td><td id='summary_{loc.replace(' ', '_')}' style='color:red; font-weight:bold;'>0.00</td><td style='width:20%;'>KW</td></tr>" for loc in selected_locs])
    summary_table_html = f"""
    <div id="summary-wrapper">
        <div id="summary-container">
            <h3>📍 장소별 당월 합계 요약</h3>
            <table id="summary-table">
                <thead><tr><th>장소명</th><th>현재 합계</th><th>단위</th></tr></thead>
                <tbody>{summary_rows}</tbody>
            </table>
        </div>
    </div>
    """
    
    all_html_content = "".join([generate_location_html(loc) for loc in selected_locs])
    bulk_js = f"const cmd = {json.dumps(st.session_state.bulk_command)}; handleBulk(cmd);" if 'bulk_command' in st.session_state else ""
    if 'bulk_command' in st.session_state: del st.session_state.bulk_command

    html_template = f"""
    {summary_table_html}
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        body {{ font-family: 'Noto Sans KR', sans-serif; background-color: #525659; display: flex; flex-direction: column; align-items: center; margin: 0; padding: 20px; }}
        
        /* 요약 표 스타일 */
        #summary-wrapper {{ width: 210mm; display: flex; justify-content: center; margin-bottom: 20px; }}
        #summary-container {{ width: 140mm; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border-top: 5px solid #FF5722; }}
        #summary-table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 13px; }}
        #summary-table th {{ background: #444; color: #fff; padding: 6px; border: 1px solid #ddd; }}
        #summary-table td {{ border: 1px solid #ddd; padding: 8px; }}

        /* 인쇄 용지 규격 (A4 정밀 고정) */
        .paper {{ 
            width: 210mm; 
            height: 296mm; /* 297mm보다 약간 작게 설정하여 여백 오류 방지 */
            background: white; 
            padding: 10mm 15mm; 
            margin-bottom: 10px; 
            box-shadow: 0 0 10px rgba(0,0,0,0.5); 
            box-sizing: border-box; 
            overflow: hidden; 
            page-break-after: always; /* 페이지 강제 전환 */
        }}
        
        .header-box {{ text-align: center; margin-bottom: 8px; }}
        .header-spacer {{ height: 15mm; }}
        .title {{ font-size: 20px; text-decoration: underline; margin-bottom: 8px; }}
        .info-row {{ display: flex; justify-content: space-between; font-size: 12px; border-bottom: 1.5px solid #000; padding-bottom: 3px; margin-bottom: 8px; }}

        table {{ width: 100%; border-collapse: collapse; border: 1.5px solid #000; table-layout: fixed; }}
        th, td {{ border: 1px solid #000; text-align: center; font-size: 10.5px; height: 25px; padding: 0; }}
        th {{ background: #f2f2f2; }}
        input {{ width: 95%; border: none; text-align: center; background: #fffde7; font-size: 11px; }}

        /* 인쇄 전용 설정 */
        @media print {{
            @page {{ size: A4; margin: 0; }}
            body {{ background: white; padding: 0; margin: 0; }}
            #summary-wrapper, .print-btn, .stAppHeader {{ display: none !important; }}
            .paper {{ 
                box-shadow: none; 
                margin: 0; 
                border: none;
                height: 297mm; 
                padding: 10mm 15mm;
            }}
            input {{ background: transparent !important; border: none; }}
        }}
        .print-btn {{ position: absolute; top: 320px; right: 10px; padding: 12px 25px; background: #FF9800; color: white; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; z-index: 1000; }}
        .save-btn {{ position: absolute; top: 320px; right: 120px; padding: 12px 25px; background: #28A745; color: white; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; z-index: 1000;}}
    </style>
    
    <script>
        function calcRow(rowId) {{
            const base = parseFloat(document.getElementById('base_' + rowId).innerText);
            const freq = parseFloat(document.getElementById('freq_' + rowId).value) || 0;
            const hour = parseFloat(document.getElementById('hour_' + rowId).value) || 0;
            const usage = base * Math.pow((freq / 60), 3) * hour;
            document.getElementById('usage_' + rowId).innerText = usage.toFixed(2);
            updateLocTotal(rowId);
        }}

        function updateLocTotal(rowId) {{
            const parts = rowId.split('_');
            const locId = parts.slice(0, parts.length - 2).join('_');
            const day = parts[parts.length - 2];
            let daySum = 0;
            ['A', 'B', 'C', 'D'].forEach(z => {{
                const el = document.getElementById('usage_' + locId + '_' + day + '_' + z);
                if(el) daySum += parseFloat(el.innerText) || 0;
            }});
            const dayTotalEl = document.getElementById('total_' + locId + '_' + day);
            if(dayTotalEl) dayTotalEl.innerText = daySum.toFixed(2);
            
            let locSum = 0;
            document.querySelectorAll('[id^="total_' + locId + '_"]').forEach(el => {{ locSum += parseFloat(el.innerText) || 0; }});
            const sEl = document.getElementById('summary_' + locId);
            if(sEl) sEl.innerText = locSum.toLocaleString(undefined, {{minimumFractionDigits: 2}});
        }}

        function handleBulk(cmd) {{
            if(cmd.type === "apply") {{
                cmd.days.forEach(d => {{
                    cmd.locs.forEach(l => {{
                        cmd.zones.forEach(z => {{
                            const id = l + "_" + d + "_" + z;
                            const fInp = document.getElementById('freq_' + id);
                            const hInp = document.getElementById('hour_' + id);
                            if(fInp) {{ fInp.value = cmd.freq; hInp.value = cmd.hour; calcRow(id); }}
                        }});
                    }});
                }});
            }} else if(cmd.type === "clear") {{
                document.querySelectorAll('input').forEach(i => i.value = "");
                document.querySelectorAll('.usage-res, .day-total').forEach(e => e.innerText = "0.00");
                document.querySelectorAll('[id^="summary_"]').forEach(e => e.innerText = "0.00");
            }}
        }}
        window.onload = function() {{ {bulk_js} }};
    </script>
    <button class="save-btn" class="btn" onclick="saveData()">💾 저장</button>
    <button class="print-btn" onclick="window.print()">🖨️ 인쇄</button>
    {all_html_content}
    """
    components.html(html_template, height=len(selected_locs) * 1600, scrolling=True)
