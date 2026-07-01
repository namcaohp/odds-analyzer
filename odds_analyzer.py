import requests
import json
import os
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
    print(f"[!] Lỗi events: {resp.status_code} - {resp.text}")
    return []

def get_odds(event_id, bookmakers='Bet365,Unibet'):
    url = f'{BASE_URL}/odds'
    params = {'apiKey': API_KEY, 'eventId': event_id, 'bookmakers': bookmakers}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    print(f"[!] Lỗi odds: {resp.status_code} - {resp.text}")
    return None

def display_events(events):
    print(f"\n[+] Tìm thấy {len(events)} trận đấu sắp diễn ra:\n")
    print(f"{'STT':<4} {'Đội nhà':<30} {'Đội khách':<30} {'ID':<12} {'Ngày giờ'}")
    print("-" * 95)
    for idx, ev in enumerate(events):
        home = ev.get('home', 'N/A')
        away = ev.get('away', 'N/A')
        eid = ev.get('id', 'N/A')
        date = ev.get('commence_time', 'N/A')[:16] if ev.get('commence_time') else 'N/A'
        print(f"{idx:<4} {home:<30} {away:<30} {eid:<12} {date}")

def save_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[+] Đã lưu file: {filename}")

def main():
    print("[*] Đang lấy danh sách môn thể thao...")
    sports = get_sports()
    if sports:
        print("[+] Các môn thể thao có sẵn:")
        for s in sports[:10]:
            print(f"  - {s.get('name')} (slug: {s.get('slug')})")
    print()

    sport_name = input("Nhập tên môn thể thao (mặc định: football): ").strip() or 'football'
    league_input = input("Nhập tên giải đấu (bỏ trống để lấy tất cả, ví dụ: fifa-world-cup): ").strip()
    league = league_input if league_input else None

    events = get_events(sport=sport_name, league=league, status='pending', limit=50)

    if not events:
        print("[!] Không có trận đấu nào sắp diễn ra. Thử lại với sport khác hoặc bỏ league.")
        return

    display_events(events)

    try:
        choice = int(input("\nNhập số thứ tự trận muốn phân tích: "))
        if choice < 0 or choice >= len(events):
            print("[!] Lựa chọn không hợp lệ.")
            return
    except ValueError:
        print("[!] Vui lòng nhập số nguyên.")
        return

    selected = events[choice]
    event_id = selected.get('id')
    if not event_id:
        print("[!] Không tìm thấy event ID.")
        return

    print(f"\n[*] Đang lấy odds cho {selected.get('home')} vs {selected.get('away')}...")
    odds_data = get_odds(event_id)

    if odds_data:
        # Chuyển dữ liệu thành chuỗi JSON đẹp
        json_str = json.dumps(odds_data, indent=2, ensure_ascii=False)
        
        # Tạo tên file
        home = selected.get('home', 'team1')
        away = selected.get('away', 'team2')
        filename = f"{home}_vs_{away}_odds.txt"
        
        # Ghi file
        save_to_file(json_str, filename)
        
        # In thông báo
        print("\n" + "="*20 + " ĐÃ LƯU FILE " + "="*20)
        print(f"Bạn có thể mở file '{filename}' để xem toàn bộ dữ liệu.")
        print("="*63)
    else:
        print("[!] Không thể lấy odds.")

if __name__ == "__main__":
    main()