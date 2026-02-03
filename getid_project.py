import requests
import csv
import sys
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# --- THÔNG TIN GITLAB ---
GITLAB_URL = "https://gitlab.atalink.com"
ACCESS_TOKEN = ""
# ------------------------

def get_all_projects():
    """Lấy thông tin tất cả các dự án từ GitLab"""
    all_projects = []
    page = 1
    per_page = 100  # Số lượng project mỗi trang (tối đa 100)
    
    while True:
        url = f"{GITLAB_URL}/api/v4/projects"
        headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}
        params = {
            "page": page,
            "per_page": per_page,
            "order_by": "created_at",
            "sort": "desc",
            "statistics": False,
            "with_custom_attributes": False
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            projects = response.json()
            
            # Nếu không còn project nào, thoát vòng lặp
            if not projects:
                break
                
            all_projects.extend(projects)
            print(f"📥 Đã tải trang {page} - {len(projects)} projects")
            page += 1
        else:
            print(f"❌ Lỗi: {response.status_code} - {response.text}")
            break
    
    return all_projects

def export_projects_to_csv(projects):
    """Xuất thông tin project ra file CSV"""
    with open('gitlab_projects.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "ID",
            "Name", 
            "Namespace",
            "Owned by",
            "Created by",
            "Created on",
            "Description",
            "Visibility",
            "Web URL"
        ])
        
        # Dữ liệu
        for p in projects:
            # Lấy namespace name (thường là tên group)
            namespace_name = p.get('namespace', {}).get('name', 'N/A')
            
            # Lấy owner name
            owner_name = p.get('owner', {}).get('name', 'N/A')
            
            # Lấy creator name
            creator_name = p.get('creator', {}).get('name', 'N/A')
            
            # Format ngày tạo
            created_at = p.get('created_at', 'N/A')
            if created_at != 'N/A':
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    created_at = dt.strftime("%b %d, %Y %I:%M%p").lower()
                except:
                    pass
            
            writer.writerow([
                p.get('id', ''),
                p.get('name', ''),
                namespace_name,
                owner_name,
                creator_name,
                created_at,
                p.get('description', ''),
                p.get('visibility', ''),
                p.get('web_url', '')
            ])

def main():
    print("🔍 Đang lấy danh sách tất cả các projects từ GitLab...")
    projects = get_all_projects()
    
    if projects:
        print(f"\n✅ Tìm thấy {len(projects)} projects")
        print("📝 Đang xuất ra file CSV...")
        export_projects_to_csv(projects)
        print("✅ Hoàn thành! File 'gitlab_projects.csv' đã sẵn sàng.\n")
        
        # Hiển thị 5 project đầu tiên
        print("📋 Mẫu dữ liệu (5 projects đầu tiên):")
        print("-" * 80)
        for i, p in enumerate(projects[:5], 1):
            namespace_name = p.get('namespace', {}).get('name', 'N/A')
            owner_name = p.get('owner', {}).get('name', 'N/A')
            creator_name = p.get('creator', {}).get('name', 'N/A')
            created_at = p.get('created_at', 'N/A')
            
            if created_at != 'N/A':
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    created_at = dt.strftime("%b %d, %Y %I:%M%p").lower()
                except:
                    pass
            
            print(f"\n{i}. Name: {p.get('name', 'N/A')}")
            print(f"   Namespace: {namespace_name}")
            print(f"   Owned by: {owner_name}")
            print(f"   Created by: {creator_name}")
            print(f"   Created on: {created_at}")
            print(f"   ID: {p.get('id', 'N/A')}")
    else:
        print("❌ Không tìm thấy project nào hoặc có lỗi xảy ra.")

if __name__ == "__main__":
    main()
