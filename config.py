import os
import sys
import configparser
from colorama import Fore, Style
from utils import get_user_documents_path, get_linux_cursor_path, get_default_driver_path, get_default_browser_path
import shutil
import datetime
import tempfile

EMOJI = {
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "SUCCESS": "✅",
    "ADMIN": "🔒",
    "ARROW": "➡️",
    "USER": "👤",
    "KEY": "🔑",
    "SETTINGS": "⚙️"
}

# global config cache
_config_cache = None

def get_config_dir(translator=None):
    """
    获取配置目录，优先级：
    1. 环境变量 CURSOR_FREE_VIP_CONFIG_DIR
    2. 配置文件 config_dir.txt（放在程序根目录）
    3. 默认文档目录
    4. 用户主目录
    """
    # 1. 环境变量
    env_dir = os.environ.get("CURSOR_FREE_VIP_CONFIG_DIR")
    if env_dir:
        config_dir = os.path.abspath(env_dir)
        try:
            os.makedirs(config_dir, exist_ok=True)
            return config_dir
        except Exception as e:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} 环境变量指定的配置目录不可用: {config_dir}，错误: {e}{Style.RESET_ALL}")

    # 2. 配置文件
    config_txt = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_dir.txt")
    if os.path.exists(config_txt):
        with open(config_txt, "r", encoding="utf-8") as f:
            file_dir = f.read().strip()
            if file_dir:
                config_dir = os.path.abspath(file_dir)
                try:
                    os.makedirs(config_dir, exist_ok=True)
                    return config_dir
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} 配置文件指定的配置目录不可用: {config_dir}，错误: {e}{Style.RESET_ALL}")

    # 3. 默认文档目录
    docs_path = get_user_documents_path()
    config_dir = os.path.normpath(os.path.join(docs_path, ".cursor-free-vip"))
    try:
        os.makedirs(config_dir, exist_ok=True)
        # 测试写入权限
        test_file = os.path.join(config_dir, "test.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return config_dir
    except Exception as e:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} 默认文档目录不可用: {config_dir}，错误: {e}{Style.RESET_ALL}")

    # 4. 用户主目录
    fallback_dir = os.path.expanduser("~/.cursor-free-vip")
    try:
        os.makedirs(fallback_dir, exist_ok=True)
        print(f"{Fore.YELLOW}{EMOJI['INFO']} 配置目录已切换到: {fallback_dir}{Style.RESET_ALL}")
        return fallback_dir
    except Exception as e:
        # 5. 临时目录
        temp_dir = os.path.join(tempfile.gettempdir(), ".cursor-free-vip")
        os.makedirs(temp_dir, exist_ok=True)
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} 配置目录已切换到临时目录: {temp_dir}{Style.RESET_ALL}")
        return temp_dir

def setup_config(translator=None):
    """Setup configuration file and return config object"""
    try:
        config_dir = get_config_dir(translator)
        config_file = os.path.normpath(os.path.join(config_dir, "config.ini"))

        # create config object
        config = configparser.ConfigParser()

        # Default configuration
        default_config = {
            'Browser': {
                'default_browser': 'chrome',
                'chrome_path': get_default_browser_path('chrome'),
                'chrome_driver_path': get_default_driver_path('chrome'),
                'edge_path': get_default_browser_path('edge'),
                'edge_driver_path': get_default_driver_path('edge'),
                'firefox_path': get_default_browser_path('firefox'),
                'firefox_driver_path': get_default_driver_path('firefox'),
                'brave_path': get_default_browser_path('brave'),
                'brave_driver_path': get_default_driver_path('brave'),
                'opera_path': get_default_browser_path('opera'),
                'opera_driver_path': get_default_driver_path('opera'),
                'operagx_path': get_default_browser_path('operagx'),
                'operagx_driver_path': get_default_driver_path('chrome')  # Opera GX 使用 Chrome 驱动
            },
            'Turnstile': {
                'handle_turnstile_time': '2',
                'handle_turnstile_random_time': '1-3'
            },
            'Timing': {
                'min_random_time': '0.1',
                'max_random_time': '0.8',
                'page_load_wait': '0.1-0.8',
                'input_wait': '0.3-0.8',
                'submit_wait': '0.5-1.5',
                'verification_code_input': '0.1-0.3',
                'verification_success_wait': '2-3',
                'verification_retry_wait': '2-3',
                'email_check_initial_wait': '4-6',
                'email_refresh_wait': '2-4',
                'settings_page_load_wait': '1-2',
                'failed_retry_time': '0.5-1',
                'retry_interval': '8-12',
                'max_timeout': '160'
            },
            'Utils': {
                'enabled_update_check': 'True',
                'enabled_force_update': 'False',
                'enabled_account_info': 'True'
            },
            'OAuth': {
                'show_selection_alert': False,  # 默认不显示选择提示弹窗
                'timeout': 120,
                'max_attempts': 3
            },
            'Token': {
                'refresh_server': 'https://token.cursorpro.com.cn',
                'enable_refresh': True
            },
            'Language': {
                'current_language': '',                'fallback_language': 'en',
                'auto_update_languages': 'True',
                'language_cache_dir': os.path.join(config_dir, "language_cache")
            }
        }

        # Add system-specific path configuration
        if sys.platform == "win32":
            appdata = os.getenv("APPDATA")
            localappdata = os.getenv("LOCALAPPDATA", "")
            default_config['WindowsPaths'] = {
                'storage_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
                'sqlite_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb"),
                'machine_id_path': os.path.join(appdata, "Cursor", "machineId"),
                'cursor_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app"),
                'updater_path': os.path.join(localappdata, "cursor-updater"),
                'update_yml_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app-update.yml"),
                'product_json_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app", "product.json")
            }
            os.makedirs(os.path.dirname(default_config['WindowsPaths']['storage_path']), exist_ok=True)

        elif sys.platform == "darwin":
            default_config['MacPaths'] = {
                'storage_path': os.path.abspath(os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/storage.json")),
                'sqlite_path': os.path.abspath(os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")),
                'machine_id_path': os.path.expanduser("~/Library/Application Support/Cursor/machineId"),
                'cursor_path': "/Applications/Cursor.app/Contents/Resources/app",
                'updater_path': os.path.expanduser("~/Library/Application Support/cursor-updater"),
                'update_yml_path': "/Applications/Cursor.app/Contents/Resources/app-update.yml",
                'product_json_path': "/Applications/Cursor.app/Contents/Resources/app/product.json"
            }
            os.makedirs(os.path.dirname(default_config['MacPaths']['storage_path']), exist_ok=True)

        elif sys.platform == "linux":
            sudo_user = os.environ.get('SUDO_USER')
            current_user = sudo_user if sudo_user else (os.getenv('USER') or os.getenv('USERNAME'))
            if not current_user:
                current_user = os.path.expanduser('~').split('/')[-1]
            if sudo_user:
                actual_home = f"/home/{sudo_user}"
                root_home = "/root"
            else:
                actual_home = f"/home/{current_user}"
                root_home = None
            if not os.path.exists(actual_home):
                actual_home = os.path.expanduser("~")
            config_base = os.path.join(actual_home, ".config")
            cursor_dir = None
            possible_paths = [
                os.path.join(config_base, "Cursor"),
                os.path.join(config_base, "cursor"),
                os.path.join(root_home, ".config", "Cursor") if root_home else None,
                os.path.join(root_home, ".config", "cursor") if root_home else None
            ]
            for path in possible_paths:
                if path and os.path.exists(path):
                    cursor_dir = path
                    break
            if not cursor_dir:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} 未找到 Cursor 相关目录于 {config_base}{Style.RESET_ALL}")
                if root_home:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} 请确保 Cursor 已安装并至少运行过一次{Style.RESET_ALL}")
            storage_path = os.path.abspath(os.path.join(cursor_dir, "User/globalStorage/storage.json")) if cursor_dir else ""
            storage_dir = os.path.dirname(storage_path) if storage_path else ""
            try:
                if storage_dir:
                    os.makedirs(storage_dir, exist_ok=True)
            except (OSError, IOError) as e:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} 无法创建存储目录: {storage_dir}，错误: {e}{Style.RESET_ALL}")
            default_config['LinuxPaths'] = {
                'storage_path': storage_path,
                'sqlite_path': os.path.abspath(os.path.join(cursor_dir, "User/globalStorage/state.vscdb")) if cursor_dir else "",
                'machine_id_path': os.path.join(cursor_dir, "machineId") if cursor_dir else "",
                'cursor_path': get_linux_cursor_path(),
                'updater_path': "",
                'update_yml_path': "",
                'product_json_path': ""
            }

        # 写入默认配置（如果文件不存在）
        if not os.path.exists(config_file):
            for section, options in default_config.items():
                config[section] = options
            with open(config_file, "w", encoding="utf-8") as f:
                config.write(f)
            print(f"{Fore.CYAN}{EMOJI['INFO']} 已创建默认配置文件: {config_file}{Style.RESET_ALL}")
        else:
            config.read(config_file, encoding="utf-8")

        global _config_cache
        _config_cache = config
        return config

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 配置初始化失败: {e}{Style.RESET_ALL}")
        raise

def get_config(translator=None):
    global _config_cache
    if _config_cache is None:
        return setup_config(translator)
    return _config_cache

def force_update_config(translator=None):
    """强制更新配置，重新从文件读取"""
    try:
        config_dir = get_config_dir(translator)
        config_file = os.path.normpath(os.path.join(config_dir, "config.ini"))
        
        if not os.path.exists(config_file):
            return setup_config(translator)
        
        config = configparser.ConfigParser()
        config.read(config_file, encoding="utf-8")
        
        # 更新全局缓存
        global _config_cache
        _config_cache = config
        
        # 验证重要配置节是否存在，若不存在则重新初始化
        required_sections = ['Browser', 'Turnstile', 'Timing', 'Utils', 'Language']
        missing_sections = [section for section in required_sections if not config.has_section(section)]
        
        if missing_sections:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} 配置文件缺少必要的节: {', '.join(missing_sections)}，重新初始化...{Style.RESET_ALL}")
            return setup_config(translator)
            
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 配置已更新{Style.RESET_ALL}")
        return config
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 强制更新配置失败: {e}{Style.RESET_ALL}")
        return setup_config(translator)

def print_config(config, translator=None):
    """打印当前配置信息"""
    if not config:
        print(f"{Fore.RED}{EMOJI['ERROR']} 配置不可用{Style.RESET_ALL}")
        return
    
    try:
        config_dir = get_config_dir(translator)
        config_file = os.path.normpath(os.path.join(config_dir, "config.ini"))
        
        print(f"\n{Fore.CYAN}{EMOJI['SETTINGS']} 配置信息:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}配置文件位置: {Style.RESET_ALL}{config_file}")
        
        for section in config.sections():
            print(f"\n{Fore.CYAN}[{section}]{Style.RESET_ALL}")
            for key, value in config.items(section):
                # 对路径类配置进行可读性处理
                if 'path' in key.lower() and os.path.exists(value):
                    display_value = f"{value} {Fore.GREEN}(存在){Style.RESET_ALL}"
                elif 'path' in key.lower() and value and not os.path.exists(value):
                    display_value = f"{value} {Fore.RED}(不存在){Style.RESET_ALL}"
                else:
                    display_value = value
                print(f"  {key} = {display_value}")
        
        print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 打印配置信息失败: {e}{Style.RESET_ALL}")