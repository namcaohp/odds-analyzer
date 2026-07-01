import streamlit as st
import requests
import json
from datetime import datetime

API_KEY = 'efcbdb5378202fe0f119d9b9eef8dce861eee79bda541d82f0b3979cb1b1e858'
BASE_URL = 'https://api.odds-api.io/v3'

def get_sports():
    url = f'{BASE_URL}/sports'
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return []

def get_events(sport='football', league=None, status='pending', limit=50):
    url = f'{BASE_URL}/events'
    params = {'apiKey': API_KEY, 'sport': sport, 'limit': limit, 'status': status}
    if league:
        params['league'] = league
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def get_odds(event_id, bookmakers='Bet365,Unibet'):
    url = f'{BASE_URL}/odds'
    params = {'apiKey': API_KEY, 'eventId': event_id, 'bookmakers': bookmakers}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    return None

st.set_page_config(page_title="Odds Analyzer", layout="wide")
st.title("⚽ Odds Analyzer - Chọn trận đấu")

# Sidebar nhập thông tin
with st.sidebar:
    st.header("Cài đặt")
    sport_name = st.text_input("Môn thể thao", value="football")
    league_input = st.text_input("Giải đấu (bỏ trống nếu không có)", placeholder="ví dụ: fifa-world-cup")
    status = st.selectbox("Trạng thái", ["pending", "live", "finished"], index=0)
    limit = st.slider("Số trận tối đa", 10, 100, 50)

# Nút tải danh sách
if st.button("📋 Lấy danh sách trận", use_container_width=True):
    with st.spinner("Đang tải danh sách trận..."):
        events = get_events(
            sport=sport_name,
            league=league_input if league_input else None,
            status=status,
            limit=limit
        )
        if events:
            st.session_state.events = events
            st.success(f"✅ Tìm thấy {len(events)} trận đấu")
        else:
            st.error("❌ Không tìm thấy trận nào. Thử đổi môn thể thao hoặc giải đấu.")

# Nếu đã có danh sách, hiển thị để chọn
if "events" in st.session_state and st.session_state.events:
    events = st.session_state.events
    options = []
    for e in events:
        home = e.get('home', '?')
        away = e.get('away', '?')
        date = e.get('commence_time', '')[:16] if e.get('commence_time') else ''
        options.append(f"{home} vs {away} - {date}")
    
    selected_index = st.selectbox("🏆 Chọn trận đấu", range(len(events)), format_func=lambda i: options[i])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Lấy odds", use_container_width=True):
            selected = events[selected_index]
            event_id = selected.get('id')
            with st.spinner("Đang lấy tỷ lệ kèo..."):
                odds_data = get_odds(event_id)
                if odds_data:
                    st.session_state.odds_data = odds_data
                    st.session_state.selected_match = selected
                    st.success("✅ Đã lấy odds thành công!")
                else:
                    st.error("❌ Không thể lấy odds. Thử lại sau.")
    
    with col2:
        if st.button("🔄 Làm mới danh sách", use_container_width=True):
            del st.session_state.events
            if "odds_data" in st.session_state:
                del st.session_state.odds_data
            st.rerun()

# Nếu có dữ liệu odds, hiển thị và cho tải file
if "odds_data" in st.session_state:
    odds_data = st.session_state.odds_data
    selected = st.session_state.selected_match
    home = selected.get('home', 'team1')
    away = selected.get('away', 'team2')
    
    st.divider()
    st.subheader("📊 Dữ liệu odds")
    
    # Tạo JSON string
    json_str = json.dumps(odds_data, indent=2, ensure_ascii=False)
    
    # Hiển thị một phần nhỏ để preview
    with st.expander("👁️ Xem trước dữ liệu", expanded=False):
        st.json(odds_data)
    
    # Nút tải file
    st.download_button(
        label="📥 Tải file JSON",
        data=json_str,
        file_name=f"{home}_vs_{away}_odds.json",
        mime="application/json",
        use_container_width=True
    )
    
    st.info(f"💡 Sao chép nội dung JSON hoặc tải file và gửi cho tôi để phân tích.")