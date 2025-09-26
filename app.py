import streamlit as st
import pandas as pd
import yaml
import os
import json
import base64
import requests
import io
from PIL import Image
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Rekap Barang dan Jasa Dinas Pertanian Lombok Barat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load CSS
load_css()

# Inisialisasi session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'home'
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

# Fungsi untuk memuat konfigurasi
def load_config():
    config_path = 'config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return json.load(file)
    else:
        # Konfigurasi default
        default_config = {
            "app_name": "Rekap Barang dan Jasa Dinas Pertanian Lombok Barat",
            "app_logo": "",
            "roles": {
                "admin": {
                    "description": "Admin dapat mengakses semua file, mengelola pengguna, mengelola link spreadsheet, serta mengedit halaman aplikasi.",
                    "access": [
                        "barang_jasa",
                        "perubahan",
                        "psp",
                        "tph",
                        "nak",
                        "bun",
                        "analisa"
                    ]
                },
                "user": {
                    "description": "User hanya bisa mengakses BUN, TPH, PSP, NAK, dan Analisa.",
                    "access": [
                        "bun",
                        "tph",
                        "psp",
                        "nak",
                        "analisa"
                    ]
                }
            },
            "spreadsheets": {
                "barang_jasa": {
                    "name": "Barang dan Jasa",
                    "url": "https://docs.google.com/spreadsheets/d/1KQ-yiIRVO1ry5LrPxGLuHxVwI8Lf8w7d_-nZolL3caM/edit?usp=drive_link",
                    "embed": True,
                    "download": True
                },
                "perubahan": {
                    "name": "Perubahan",
                    "url": "https://docs.google.com/spreadsheets/d/1mNUWRZsff0sl9ZktRQFxYqEcIzzsqcNI/edit?usp=drive_link",
                    "embed": True,
                    "download": True
                },
                "psp": {
                    "name": "PSP",
                    "url": "https://docs.google.com/spreadsheets/d/1Fqn_g6FSy1Em3Lz90esuQLAetA0TQfhS/edit?usp=drive_link",
                    "embed": True,
                    "download": True
                },
                "tph": {
                    "name": "TPH",
                    "url": "https://docs.google.com/spreadsheets/d/1l7nKhV7LDzvETPOOdRMK25i5whVf5iUb/edit?usp=drive_link",
                    "embed": True,
                    "download": True
                },
                "nak": {
                    "name": "NAK",
                    "url": "https://docs.google.com/spreadsheets/d/19F-VlNJcGGDctCfG7Fg0jpN7bYcjunGX/edit?usp=drive_link",
                    "embed": True,
                    "download": True
                },
                "bun": {
                    "name": "BUN",
                    "url": "https://docs.google.com/spreadsheets/d/1ujyWx5hKlhpVH-_8_89whG9wgy2KVT6h/edit?usp=drive_link",
                    "embed": True,
                    "download": True
                },
                "analisa": {
                    "name": "Analisa",
                    "url": "https://docs.google.com/spreadsheets/d/1HrcReS9fHohnWzptsILGsaW01Mt55LSPaf44Lq8-A2Q/edit?usp=drive_link",
                    "embed": True,
                    "download": True
                }
            },
            "features": {
                "embed_spreadsheet": True,
                "inline_editing": True,
                "download_button": True,
                "user_management": True,
                "link_management": True,
                "page_editing": True
            }
        }
        
        # Simpan konfigurasi default
        with open(config_path, 'w') as file:
            json.dump(default_config, file, indent=2)
        
        return default_config

# Muat konfigurasi
config = load_config()

# Fungsi untuk memuat kredensial pengguna
def load_credentials():
    credentials_path = 'credentials.yaml'
    if os.path.exists(credentials_path):
        with open(credentials_path, 'r') as file:
            return yaml.load(file, Loader=SafeLoader)
    else:
        # Kredensial default
        default_credentials = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@example.com',
                        'name': 'Admin',
                        'password': stauth.Hasher(['admin']).generate()[0],
                        'role': 'admin'
                    },
                    'user': {
                        'email': 'user@example.com',
                        'name': 'User',
                        'password': stauth.Hasher(['user']).generate()[0],
                        'role': 'user'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'barjas_app_cookie',
                'name': 'barjas_app_cookie'
            }
        }
        
        # Simpan kredensial default
        with open(credentials_path, 'w') as file:
            yaml.dump(default_credentials, file)
        
        return default_credentials

# Muat kredensial
credentials = load_credentials()

# Inisialisasi authenticator sekali saja (global)
authenticator = stauth.Authenticate(
    credentials['credentials'],
    credentials['cookie']['name'],
    credentials['cookie']['key'],
    credentials['cookie']['expiry_days']
)

# Fungsi untuk menyimpan kredensial
def save_credentials(credentials):
    with open('credentials.yaml', 'w') as file:
        yaml.dump(credentials, file)

# Fungsi untuk menyimpan konfigurasi
def save_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=2)

# Fungsi untuk mengunduh file dari Google Sheets
def download_spreadsheet(url, filename):
    try:
        # Mengubah URL untuk mengunduh sebagai Excel
        if "docs.google.com/spreadsheets" in url:
            # Ekstrak ID spreadsheet
            if "/d/" in url and "/edit" in url:
                sheet_id = url.split("/d/")[1].split("/edit")[0]
            elif "/d/" in url and "/view" in url:
                sheet_id = url.split("/d/")[1].split("/view")[0]
            else:
                return None, "Format URL tidak valid"
            
            # URL untuk mengunduh sebagai Excel
            export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
            
            # Unduh file
            response = requests.get(export_url)
            if response.status_code == 200:
                return response.content, None
            else:
                return None, f"Gagal mengunduh file: {response.status_code}"
        else:
            return None, "URL bukan Google Spreadsheet"
    except Exception as e:
        return None, f"Error: {str(e)}"

# Fungsi untuk menghasilkan link download
def get_download_button(url, filename):
    """Generates a download button for the file"""
    content, error = download_spreadsheet(url, filename)
    
    if error:
        return f'<p style="color: red;">Error: {error}</p>'
    
    b64 = base64.b64encode(content).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-btn"><i class="fas fa-download"></i> Download Spreadsheet</a>'
    return href

# Fungsi untuk menampilkan iframe spreadsheet
def display_spreadsheet(url):
    """Displays the spreadsheet in an iframe with responsive design"""
    iframe_html = f'''
    <div class="iframe-container">
        <iframe class="responsive-iframe" src="{url}/preview" frameborder="0"></iframe>
    </div>
    '''
    st.markdown(iframe_html, unsafe_allow_html=True)

# Fungsi untuk menampilkan halaman berdasarkan role
def show_page(page_id):
    if page_id not in config['spreadsheets']:
        st.error(f"Halaman {page_id} tidak ditemukan.")
        return
    
    # Cek akses pengguna
    if st.session_state['role'] != 'admin' and page_id not in config['roles'][st.session_state['role']]['access']:
        st.error("Anda tidak memiliki akses ke halaman ini.")
        return
    
    spreadsheet = config['spreadsheets'][page_id]
    st.title(spreadsheet['name'])
    
    # Tampilkan spreadsheet
    if spreadsheet['embed']:
        display_spreadsheet(spreadsheet['url'])
    
    # Tombol download
    if spreadsheet['download']:
        st.markdown(get_download_button(spreadsheet['url'], f"{spreadsheet['name']}.xlsx"), unsafe_allow_html=True)

# Fungsi untuk menampilkan halaman admin
def show_admin_page():
    st.title("Halaman Admin")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Manajemen Pengguna", "Manajemen Link", "Pengaturan Aplikasi", "Logo Aplikasi"])
    
    with tab1:
        st.header("Manajemen Pengguna")
        
        # Tampilkan daftar pengguna
        st.subheader("Daftar Pengguna")
        users_data = []
        for username, user_info in credentials['credentials']['usernames'].items():
            users_data.append({
                'Username': username,
                'Nama': user_info['name'],
                'Email': user_info['email'],
                'Role': user_info['role']
            })
        
        users_df = pd.DataFrame(users_data)
        st.dataframe(users_df)
        
        # Form tambah pengguna
        st.subheader("Tambah Pengguna Baru")
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_name = st.text_input("Nama")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["admin", "user"])
            
            submit_button = st.form_submit_button("Tambah Pengguna")
            
            if submit_button:
                if new_username in credentials['credentials']['usernames']:
                    st.error("Username sudah digunakan.")
                else:
                    credentials['credentials']['usernames'][new_username] = {
                        'email': new_email,
                        'name': new_name,
                        'password': stauth.Hasher([new_password]).generate()[0],
                        'role': new_role
                    }
                    save_credentials(credentials)
                    st.success("Pengguna berhasil ditambahkan.")
                    st.experimental_rerun()
        
        # Form hapus pengguna
        st.subheader("Hapus Pengguna")
        with st.form("delete_user_form"):
            username_to_delete = st.selectbox("Pilih Username", list(credentials['credentials']['usernames'].keys()))
            delete_button = st.form_submit_button("Hapus Pengguna")
            
            if delete_button:
                if username_to_delete == st.session_state['username']:
                    st.error("Anda tidak dapat menghapus akun yang sedang digunakan.")
                else:
                    del credentials['credentials']['usernames'][username_to_delete]
                    save_credentials(credentials)
                    st.success("Pengguna berhasil dihapus.")
                    st.experimental_rerun()
    
    with tab2:
        st.header("Manajemen Link Spreadsheet")
        
        # Tampilkan daftar spreadsheet
        st.subheader("Daftar Spreadsheet")
        spreadsheets_data = []
        for sheet_id, sheet_info in config['spreadsheets'].items():
            spreadsheets_data.append({
                'ID': sheet_id,
                'Nama': sheet_info['name'],
                'URL': sheet_info['url'],
                'Embed': sheet_info['embed'],
                'Download': sheet_info['download']
            })
        
        spreadsheets_df = pd.DataFrame(spreadsheets_data)
        st.dataframe(spreadsheets_df)
        
        # Form edit spreadsheet
        st.subheader("Edit Spreadsheet")
        with st.form("edit_spreadsheet_form"):
            sheet_to_edit = st.selectbox("Pilih Spreadsheet", list(config['spreadsheets'].keys()))
            new_name = st.text_input("Nama Baru", value=config['spreadsheets'][sheet_to_edit]['name'])
            new_url = st.text_input("URL Baru", value=config['spreadsheets'][sheet_to_edit]['url'])
            new_embed = st.checkbox("Embed", value=config['spreadsheets'][sheet_to_edit]['embed'])
            new_download = st.checkbox("Download", value=config['spreadsheets'][sheet_to_edit]['download'])
            
            edit_button = st.form_submit_button("Simpan Perubahan")
            
            if edit_button:
                config['spreadsheets'][sheet_to_edit]['name'] = new_name
                config['spreadsheets'][sheet_to_edit]['url'] = new_url
                config['spreadsheets'][sheet_to_edit]['embed'] = new_embed
                config['spreadsheets'][sheet_to_edit]['download'] = new_download
                save_config(config)
                st.success("Spreadsheet berhasil diperbarui.")
                st.experimental_rerun()
    
    with tab3:
        st.header("Pengaturan Aplikasi")
        
        # Form edit nama aplikasi
        st.subheader("Edit Nama Aplikasi")
        with st.form("edit_app_name_form"):
            new_app_name = st.text_input("Nama Aplikasi", value=config['app_name'])
            save_app_name_button = st.form_submit_button("Simpan Nama Aplikasi")
            
            if save_app_name_button:
                config['app_name'] = new_app_name
                save_config(config)
                st.success("Nama aplikasi berhasil diperbarui.")
                st.experimental_rerun()
        
        # Form edit fitur
        st.subheader("Edit Fitur")
        with st.form("edit_features_form"):
            embed_spreadsheet = st.checkbox("Embed Spreadsheet", value=config['features']['embed_spreadsheet'])
            inline_editing = st.checkbox("Inline Editing", value=config['features']['inline_editing'])
            download_button = st.checkbox("Download Button", value=config['features']['download_button'])
            user_management = st.checkbox("User Management", value=config['features']['user_management'])
            link_management = st.checkbox("Link Management", value=config['features']['link_management'])
            page_editing = st.checkbox("Page Editing", value=config['features']['page_editing'])
            
            save_features_button = st.form_submit_button("Simpan Fitur")
            
            if save_features_button:
                config['features']['embed_spreadsheet'] = embed_spreadsheet
                config['features']['inline_editing'] = inline_editing
                config['features']['download_button'] = download_button
                config['features']['user_management'] = user_management
                config['features']['link_management'] = link_management
                config['features']['page_editing'] = page_editing
                save_config(config)
                st.success("Fitur berhasil diperbarui.")
                st.experimental_rerun()
    
    with tab4:
        st.header("Logo Aplikasi")
        
        # Tampilkan logo saat ini jika ada
        if config.get('app_logo'):
            st.subheader("Logo Saat Ini")
            st.image(config['app_logo'], width=150)
        
        # Form untuk mengunggah logo baru
        st.subheader("Unggah Logo Baru")
        uploaded_file = st.file_uploader("Pilih file gambar", type=['png', 'jpg', 'jpeg', 'svg'])
        
        if uploaded_file is not None:
            # Tampilkan preview
            st.subheader("Preview Logo")
            st.image(uploaded_file, width=150)
            
            # Tombol simpan
            if st.button("Simpan Logo"):
                # Konversi gambar ke base64
                bytes_data = uploaded_file.getvalue()
                encoded = base64.b64encode(bytes_data).decode()
                
                # Simpan ke konfigurasi
                mime_type = uploaded_file.type
                config['app_logo'] = f"data:{mime_type};base64,{encoded}"
                save_config(config)
                st.success("Logo berhasil disimpan.")
                st.experimental_rerun()

# Fungsi untuk menampilkan halaman beranda
def show_home_page():
    st.title(config['app_name'])
    
    if 'username' in st.session_state and st.session_state['username'] is not None:
        username = st.session_state['username']
        name = credentials['credentials']['usernames'][username]['name']
        role = st.session_state.get('role', 'guest')
        
        st.write(f"Selamat datang, {name}!")
        
        st.markdown("""
        ### Tentang Aplikasi
        Aplikasi ini digunakan untuk mengelola dan melihat data Barang dan Jasa Dinas Pertanian Lombok Barat.
        
        ### Cara Penggunaan
        1. Pilih menu yang tersedia di sidebar sesuai dengan kebutuhan Anda.
        2. Anda dapat melihat dan mengunduh data sesuai dengan hak akses yang dimiliki.
        """)
        
        # Tampilkan informasi role
        st.subheader("Informasi Pengguna")
        st.write(f"**Username:** {username}")
        st.write(f"**Role:** {role}")
        
        if role in config['roles'] and 'description' in config['roles'][role]:
            st.write(f"**Deskripsi Role:** {config['roles'][role]['description']}")
    else:
        st.write("Selamat datang, Pengunjung!")
        
        st.markdown("""
        ### Tentang Aplikasi
        Aplikasi ini digunakan untuk mengelola dan melihat data Barang dan Jasa Dinas Pertanian Lombok Barat.
        
        ### Silakan login untuk mengakses fitur aplikasi
        """)
    
    # Tampilkan daftar akses
    st.subheader("Daftar Akses")
    # Periksa apakah role ada dan valid
    role = st.session_state.get('role')
    if role and role in config.get('roles', {}):
        access_list = config['roles'][role].get('access', [])
        for access in access_list:
            if access in config.get('spreadsheets', {}):
                st.write(f"- {config['spreadsheets'][access]['name']}")
    else:
        st.info("Silakan login untuk melihat daftar akses yang tersedia.")

# Fungsi untuk menampilkan sidebar
# Fungsi untuk menampilkan sidebar
# Fungsi untuk menampilkan sidebar
def show_sidebar():
    with st.sidebar:
        # Header
        st.markdown("""<div class="app-header">""", unsafe_allow_html=True)

        if config.get('app_logo'):
            st.markdown(
                f'<div class="logo-container"><img src="{config["app_logo"]}" class="app-logo" alt="Logo"></div>',
                unsafe_allow_html=True
            )

        st.markdown("<h2>📊 Menu Navigasi</h2>", unsafe_allow_html=True)

        # Info user login
        if (
            st.session_state.get('authenticated')
            and st.session_state.get('username') in credentials['credentials']['usernames']
        ):
            username = st.session_state.get('username')
            user_info = credentials['credentials']['usernames'][username]
            name = user_info.get('name', username)
            role = st.session_state.get('role', 'user')

            st.markdown(f"""
            <div class="card">
                <p>Selamat datang,</p>
                <h3>{name}</h3>
                <span class="badge badge-{role}">{role.upper()}</span>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="card">
                <p>Silakan login</p>
            </div>
            """, unsafe_allow_html=True)
            name = "Guest"
            role = "guest"

        # Menu umum
        if st.button("🏠 Beranda"):
            st.session_state['current_page'] = 'home'
            st.experimental_rerun()

        # Menu admin (khusus admin)
        if st.session_state.get('role') == 'admin':
            if st.button("⚙️ Admin Panel"):
                st.session_state['current_page'] = 'admin'
                st.experimental_rerun()

        # Menu spreadsheet
        st.markdown("<h3>📑 Spreadsheet</h3>", unsafe_allow_html=True)
        role = st.session_state.get('role', 'guest')
        for sheet_id, sheet_info in config['spreadsheets'].items():
            if role == 'admin' or (
                role in config['roles']
                and sheet_id in config['roles'][role]['access']
            ):
                if st.button(f"📄 {sheet_info['name']}"):
                    st.session_state['current_page'] = sheet_id
                    st.experimental_rerun()

        # Toggle tema
        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Tema:")
        with col2:
            if st.session_state['theme'] == 'light':
                if st.button("🌙"):
                    st.session_state['theme'] = 'dark'
                    st.experimental_rerun()
            else:
                if st.button("☀️"):
                    st.session_state['theme'] = 'light'
                    st.experimental_rerun()

        # === Tombol Logout tetap di sidebar, hanya muncul kalau sudah login ===
        if st.session_state.get('authenticated'):
            try:
                authenticator.logout("🚪 Logout", "sidebar")
            except KeyError:
                # fallback reset session
                st.session_state['authenticated'] = False
                st.session_state['username'] = None
                st.session_state['role'] = None
                st.session_state['current_page'] = 'home'
                st.session_state['theme'] = 'light'
                st.session_state['authentication_status'] = None

# Fungsi untuk menampilkan halaman login
def show_login_page():
    st.title(config['app_name'])
    
    
    name, authentication_status, username = authenticator.login(
    fields={"Form name": "Login"},
    location="main"
)

    
    if authentication_status:
        st.session_state['authenticated'] = True
        st.session_state['username'] = username
        st.session_state['role'] = credentials['credentials']['usernames'][username]['role']
        st.experimental_rerun()
    elif authentication_status == False:
        st.error('Username/password salah')
    elif authentication_status == None:
        st.warning('Silakan masukkan username dan password')

# Main app
def main():
    # Pastikan semua session_state utama ada
    for key, val in {
        "authenticated": False,
        "username": None,
        "role": "guest",
        "current_page": "home",
        "theme": "light",
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    if not st.session_state["authenticated"]:
        # === Halaman login cantik ===
        logo_html = ""
        if config.get("app_logo"):
            logo_html = f'<img src="{config["app_logo"]}" class="login-logo" alt="Logo">'
        else:
            # fallback kalau logo belum diupload
            logo_html = '<img src="https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg" class="login-logo" alt="Logo">'

        st.markdown(f"""
<style>
.login-container {{
    text-align: center;
    margin-bottom: 20px;
}}
.login-logo {{
    width: 120px;
    height: auto;
    margin-bottom: 15px;
}}
.login-card {{
    max-width: 400px;
    margin: 0 auto;
    padding: 30px;
    border-radius: 15px;
    background-color: #f9f9f9;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    text-align: center;
}}
.marquee {{
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    box-sizing: border-box;
    color: #007BFF;
    font-weight: bold;
    font-size: 18px;
    margin-top: 10px;
}}
.marquee span {{
    display: inline-block;
    padding-left: 100%;
    animation: marquee 10s linear infinite;
}}
@keyframes marquee {{
    0%   {{ transform: translate(0, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}
</style>

<div class="login-container">
    {logo_html}
    <h2>Silakan Login</h2>
    <div class="marquee"><span> REKAP BARANG DAN JASA DINAS PERTANIAN KABUPATEN LOMBOK BARAT TAHUN 2025 </span></div>
</div>
<div class="login-card">
""", unsafe_allow_html=True)


        # Form login
        name, authentication_status, username = authenticator.login("Login", "main")

        if authentication_status:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = credentials["credentials"]["usernames"][username]["role"]
            st.experimental_rerun()
        elif authentication_status is False:
            st.error("Username atau password salah.")
        else:
            st.info("Masukkan username dan password Anda.")

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # === Sudah login → tampilkan sidebar + halaman ===
        show_sidebar()

        if st.session_state["current_page"] == "home":
            show_home_page()
        elif st.session_state["current_page"] == "admin":
            if st.session_state["role"] == "admin":
                show_admin_page()
            else:
                st.error("Anda tidak memiliki akses ke halaman ini.")
                st.session_state["current_page"] = "home"
                st.experimental_rerun()
        else:
            show_page(st.session_state["current_page"])


if __name__ == "__main__":
    main()

    
    # Footer
st.markdown("""
<div class="footer">
    <p>© 2023 Dinas Pertanian Lombok Barat</p>
</div>
</div>
""", unsafe_allow_html=True)
