import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import json
import os

# 페이지 설정
st.set_page_config(
    page_title="☕ 실시간 카페 주문",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    .main-order-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .menu-upload-section {
        background: #f0f8f0;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #28a745;
        margin: 10px 0;
    }
    
    .sidebar-section {
        background: transparent;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: none;
    }
    
    .menu-image-main {
        border: 3px solid #007bff;
        border-radius: 10px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# 주문 데이터 파일
ORDERS_FILE = "realtime_orders.json"

# 세션 상태 초기화
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'menu_image' not in st.session_state:
    st.session_state.menu_image = None
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = ""

def load_orders():
    """주문 데이터 로드"""
    try:
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                st.session_state.orders = data.get('orders', [])
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")

def save_orders():
    """주문 데이터 저장"""
    try:
        data = {
            'orders': st.session_state.orders,
            'last_updated': datetime.now().isoformat()
        }
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def add_order(name, items, note=""):
    """주문 추가/수정"""
    if not name.strip() or not items.strip():
        return False
    
    items_list = [item.strip() for item in items.split(',') if item.strip()]
    
    # 기존 주문 수정
    for i, order in enumerate(st.session_state.orders):
        if order['name'] == name:
            st.session_state.orders[i] = {
                'timestamp': datetime.now().strftime('%H:%M'),
                'name': name,
                'items': items_list,
                'note': note,
                'order_time': datetime.now().isoformat()
            }
            save_orders()
            return True
    
    # 새 주문 추가
    st.session_state.orders.append({
        'timestamp': datetime.now().strftime('%H:%M'),
        'name': name,
        'items': items_list,
        'note': note,
        'order_time': datetime.now().isoformat()
    })
    save_orders()
    return True

def main():
    load_orders()
    
    st.title("☕ 팀 카페 주문")
    
    # 메인 레이아웃: 왼쪽 메인 / 오른쪽 슬림
    col1, col2 = st.columns([3.2, 0.8])
    
    # 왼쪽 메인 영역
    with col1:
        # 🎯 메뉴판 표시 (맨 위)
        st.markdown("## 📋 카페 메뉴판")
        
        if st.session_state.menu_image is not None:
            st.markdown('<div class="menu-image-main">', unsafe_allow_html=True)
            st.image(st.session_state.menu_image, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📸 아래 업로드 버튼을 통해 메뉴판 사진을 올려주세요!")
        
        # 주문 섹션
        st.markdown('<div class="main-order-section">', unsafe_allow_html=True)
        st.markdown("## 🛒 주문하기")
        
        # 빠른선택 (form 바깥에서)
        col_name1, col_name2 = st.columns([2, 1])
        
        with col_name2:
            quick_name = st.selectbox(
                "빠른선택", 
                ["직접입력", "박광우", "김성한", "김영민", "노주연", "박용운", "백용진", "이영호", "이한승", "장환준", "김세환", "배한성", "성용", "신기욱", "정지안", "조우석"]
            )
            if quick_name != "직접입력":
                st.session_state.selected_name = quick_name
        
        with st.form("main_order_form", clear_on_submit=False):
            # 이름 입력 행 (form 내부)
            with col_name1:
                name = st.text_input(
                    "👤 이름", 
                    value=st.session_state.selected_name, 
                    placeholder="이름을 입력하세요"
                )
            
            # 메뉴 입력
            menu_items = st.text_area(
                "☕ 주문 메뉴", 
                placeholder="위 메뉴판을 보면서 입력하세요!\n\n예: 아메리카노 ICE, 바닐라라떼, 크루아상",
                height=80
            )
            
            # 요청사항과 버튼을 한 줄에
            col_note, col_btn = st.columns([2, 1])
            
            with col_note:
                note = st.text_input("💬 요청사항", placeholder="샷추가, 연하게 등")
            
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("🛒 주문완료", use_container_width=True, type="primary")
            
            if submitted:
                if add_order(name, menu_items, note):
                    st.success("✅ 주문이 완료되었습니다!")
                    st.balloons()
                    st.session_state.selected_name = ""
                else:
                    st.error("⚠️ 이름과 메뉴를 입력해주세요!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    
    # 오른쪽 슬림 사이드바
    with col2:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        
        # 새로고침 버튼과 멘트 (현황 위)
        col_refresh, col_space = st.columns([1, 2])
        with col_refresh:
            if st.button("🔄", use_container_width=True, help="새로고침"):
                load_orders()
                st.rerun()
        with col_space:
            st.markdown("<small>💡 최신 주문 확인</small>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**📊 현황**")
        
        # 현황 메트릭
        if st.session_state.orders:
            total_people = len(st.session_state.orders)
            total_items = sum(len(order['items']) for order in st.session_state.orders)
            latest_time = st.session_state.orders[-1]['timestamp']
        else:
            total_people = 0
            total_items = 0
            latest_time = "-"
        
        st.metric("👥 주문인원", f"{total_people}명")
        st.metric("📋 총메뉴", f"{total_items}개")
        st.metric("⏰ 최근주문", latest_time)
        
        st.markdown("---")
        
        # 메뉴 집계 (먼저)
        if st.session_state.orders:
            st.markdown("**📄 집계**")
            
            menu_count = {}
            for order in st.session_state.orders:
                for item in order['items']:
                    menu_count[item] = menu_count.get(item, 0) + 1
            
            top_menus = sorted(menu_count.items(), key=lambda x: x[1], reverse=True)[:3]
            for menu, count in top_menus:
                display_menu = menu[:10] + "..." if len(menu) > 10 else menu
                st.markdown(f"<small>• {display_menu}: {count}개</small>", unsafe_allow_html=True)
            
            if len(menu_count) > 3:
                st.markdown(f"<small>... 외 {len(menu_count)-3}개</small>", unsafe_allow_html=True)
            
            st.markdown("---")
        
        # 주문 목록 (나중)
        st.markdown("**📋 주문목록**")
        
        if not st.session_state.orders:
            st.info("주문 없음")
        else:
            for i, order in enumerate(reversed(st.session_state.orders)):
                col_info, col_del = st.columns([2.5, 0.5])
                
                with col_info:
                    st.markdown(f"**{order['name']}**")
                    st.markdown(f"<small>{order['timestamp']}</small>", unsafe_allow_html=True)
                    for item in order['items'][:2]:
                        st.markdown(f"<small>• {item}</small>", unsafe_allow_html=True)
                    if len(order['items']) > 2:
                        st.markdown(f"<small>• +{len(order['items'])-2}개</small>", unsafe_allow_html=True)
                    if order.get('note'):
                        st.markdown(f"<small>💬 {order['note']}</small>", unsafe_allow_html=True)
                
                with col_del:
                    if st.button("❌", key=f"del_{i}", help="삭제"):
                        original_idx = len(st.session_state.orders) - 1 - i
                        st.session_state.orders.pop(original_idx)
                        save_orders()
                        st.rerun()
                
                st.markdown("<hr style='margin: 5px 0; border: 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        
        st.markdown('---')
        
        # 📤 메뉴판 업로드 (맨 아래)
        st.markdown("**📤 메뉴판 업로드**")
        
        uploaded_file = st.file_uploader(
            "메뉴판 사진", 
            type=['png', 'jpg', 'jpeg'],
            key="menu_upload",
            help="메뉴판 이미지 업로드 (PNG, JPG, JPEG)"
        )
        
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.session_state.menu_image = image
                st.success("✅ 메뉴판이 업로드되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"이미지 로드 오류: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
