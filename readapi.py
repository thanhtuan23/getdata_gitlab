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

ROLE_MAP = {
    10: "Guest",
    20: "Reporter",
    30: "Developer",
    40: "Maintainer", 
    50: "Owner"
}

def load_projects():
    """Đọc danh sách projects từ file CSV"""
    projects = []
    try:
        with open('gitlab_projects.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                projects.append({
                    'id': row['ID'],
                    'name': row['Name'],
                    'namespace': row['Namespace']
                })
        return projects
    except FileNotFoundError:
        print("❌ Không tìm thấy file gitlab_projects.csv!")
        print("💡 Hãy chạy getid_project.py trước để tạo file này.")
        return []

def get_project_members(project_id):
    """Lấy danh sách members của một project (với pagination)"""
    all_members = []
    page = 1
    per_page = 100  # Lấy tối đa 100 members mỗi trang
    
    while True:
        url = f"{GITLAB_URL}/api/v4/projects/{project_id}/members/all"
        headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}
        params = {
            "page": page,
            "per_page": per_page
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            members = response.json()
            
            # Nếu không còn members nào, thoát vòng lặp
            if not members:
                break
            
            all_members.extend(members)
            page += 1
        else:
            # Nếu gặp lỗi, trả về None
            return None
    
    return all_members

def export_all_members():
    """Xuất members của tất cả các projects ra file CSV"""
    projects = load_projects()
    
    if not projects:
        return
    
    print(f"📋 Tìm thấy {len(projects)} projects")
    print(f"🔍 Đang lấy thông tin members từ tất cả các projects...\n")
    
    all_members_data = []
    project_count = 0
    
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        project_namespace = project['namespace']
        
        members = get_project_members(project_id)
        
        if members is not None:
            member_count = len(members)
            if member_count > 0:
                project_count += 1
                print(f"✓ [{project_count}/{len(projects)}] {project_name} - {member_count} members")
                
                for m in members:
                    # Lọc bỏ blocked và banned users
                    user_state = m.get('state', '')
                    if user_state in ['blocked', 'banned']:
                        continue  # Bỏ qua user này
                    
                    # Format expires_at date
                    expires_at = m.get('expires_at', 'N/A')
                    if expires_at and expires_at != 'N/A':
                        try:
                            dt = datetime.strptime(expires_at, "%Y-%m-%d")
                            expires_at = dt.strftime("%b %d, %Y")
                        except:
                            pass
                    
                    all_members_data.append({
                        'project_id': project_id,
                        'project_name': project_name,
                        'project_namespace': project_namespace,
                        'user_id': m.get('id', ''),
                        'username': m.get('username', ''),
                        'name': m.get('name', ''),
                        # 'email': m.get('email', 'N/A'),
                        'role': ROLE_MAP.get(m.get('access_level'), 'Unknown'),
                        'access_level': m.get('access_level', ''),
                        'state': m.get('state', ''),
                        # 'expires_at': expires_at,
                        # 'created_at': m.get('created_at', 'N/A'),
                        'created_by': m.get('created_by', {}).get('name', 'N/A')
                    })
            else:
                print(f"○ [{project_count}/{len(projects)}] {project_name} - không có members")
        else:
            print(f"✗ [{project_count}/{len(projects)}] {project_name} - lỗi khi lấy dữ liệu")
    
    # Xuất ra file CSV
    if all_members_data:
        print(f"\n📝 Đang xuất {len(all_members_data)} members ra file CSV...")
        
        with open('gitlab_all_members.csv', 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = [
                'project_id', 'project_name', 'project_namespace',
                'user_id', 'username', 'name', 'email',
                'role', 'access_level', 'state', 'expires_at', 'created_at', 'created_by'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_members_data)
        
        print("✅ Hoàn thành! File 'gitlab_all_members.csv' đã sẵn sàng.")
        print(f"\n📊 Thống kê:")
        print(f"   - Tổng số projects có members: {project_count}")
        print(f"   - Tổng số members (có thể trùng): {len(all_members_data)}")
        
        # Hiển thị 5 ví dụ
        print(f"\n📋 Mẫu dữ liệu (5 dòng đầu tiên):")
        print("-" * 100)
        for i, member in enumerate(all_members_data[:5], 1):
            print(f"\n{i}. Project: {member['project_name']} (ID: {member['project_id']})")
            print(f"   Namespace: {member['project_namespace']}")
            print(f"   User: {member['name']} (@{member['username']})")
            print(f"   Email: {member['email']}")
            print(f"   Role: {member['role']} (Level: {member['access_level']})")
            print(f"   State: {member['state']}")
            print(f"   Expires: {member['expires_at']}")
            print(f"   Created by: {member['created_by']}")
    else:
        print("\n⚠️ Không có dữ liệu members nào được tìm thấy.")

def main():
    export_all_members()

if __name__ == "__main__":
    main()