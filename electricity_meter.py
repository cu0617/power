import streamlit as st
import streamlit.components.v1 as components

def show_electricity_meter(date_str):
    st.subheader("⚡ 전기실 계량기 검침표")
    
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
    selected_targets = st.multiselect("🚨 집중 확인 판넬 선택", all_panel_names, default=default_targets)

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
                <td><input type='number' class='inp-meter' data-panel='{safe_id}' oninput='syncInput(this)' placeholder='-'></td>
                <td class='bg'>{m}</td>
            </tr>"""
        return f"<table><thead><tr><th width='18%'>비 고</th><th width='25%'>판넬명</th><th width='42%'>당월지침</th><th width='15%'>배율</th></tr></thead><tbody>{rows}</tbody></table>"

    half = (len(data) + 1) // 2
    
    html_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 20px; background-color: #525659; display: flex; flex-direction: column; align-items: center; }}
        
        /* 고정 버튼 공통 스타일 */
        .btn {{ 
            position: fixed; 
            padding: 12px 25px; 
            border: none; 
            border-radius: 50px; 
            cursor: pointer; 
            font-weight: bold; 
            color: white; 
            z-index: 9999; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            transition: 0.2s;
        }}
        .btn:hover {{ opacity: 0.8; transform: translateY(-2px); }}

        /* 개별 버튼 위치 */
        #btn-save {{ position: absolute; top: 270px; right: 130px; background: #28A745; }}
        #btn-print {{ position: absolute; top: 270px; right: 20px; background: #FF9800; }}
        #btn-reset {{ position: absolute; top: 270px; left: 20px; background: #444; }}

        .container {{ width: 210mm; display: flex; flex-direction: column; align-items: center; }}
        .summary-section {{ width: 100%; margin-bottom: 20px; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border-top: 5px solid #ff5722; box-sizing: border-box; }}
        .summary-section h3 {{ margin: 0 0 10px 0; color: #ff5722; font-size: 15px; text-align: center; }}
        
        .paper {{ width: 210mm; height: 296mm; background: white; padding: 10mm; color: black; box-sizing: border-box; box-shadow: 0 0 15px rgba(0,0,0,0.5); overflow: hidden; }}
        h2 {{ text-align: center; margin: 0 0 10px 0; font-size: 18px; text-decoration: underline; }}
        .info {{ display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 8px; border-bottom: 2px solid #000; padding-bottom: 5px; }}
        
        .inp-name {{ border: none; border-bottom: 1px dotted #000; width: 80px; text-align: center; background: #fffde7; }}
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
            .inp-meter, .inp-name {{ background: transparent !important; border: none; color: blue !important; }}
        }}
    </style>
    
    <script>
        function syncInput(el) {{
            const panelId = el.getAttribute('data-panel');
            const val = el.value;
            const targets = document.querySelectorAll(`input[data-panel="${{panelId}}"]`);
            targets.forEach(target => {{ if (target !== el) target.value = val; }});
        }}

        function resetData() {{
            if(confirm("모든 당월지침 데이터를 초기화하시겠습니까?")) {{
                document.querySelectorAll('.inp-meter, .inp-name').forEach(input => input.value = "");
            }}
        }}
    </script>
    <button id="btn-save" class="btn" onclick="saveData()">💾 저장</button>
    <button id="btn-print" class="btn" onclick="window.print()">🖨️ 인쇄</button>
    <button id="btn-reset" class="btn" onclick="resetData()">🗑️ 데이터 초기화</button>

    <div class="container">
        <div class="summary-section">
            <h3>🚨 주요 계량기 집중 확인 (지침 동기화)</h3>
            {make_table(summary_data, is_summary=True)}
        </div>

        <div class="paper">
            <h2>전기실 계량기 검침표</h2>
            <div class="info">
                <span>검침 일자: {date_str}</span>
                <span>점검자: <input type="text" class="inp-name" placeholder="성명"> (인)</span>
            </div>
            <div class="cnt">
                <div>{make_table(data[:half])}</div>
                <div style="width: 1%"></div> <div>{make_table(data[half:])}</div>
            </div>
        </div>
    </div>
    """
    components.html(html_code, height=1350, scrolling=True)
