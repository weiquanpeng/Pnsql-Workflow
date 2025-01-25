import yaml
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent  # 定位到项目根目录


# 加载 YAML 配置文件
def load_config():
    config_path = BASE_DIR / "config.yaml"  # 定位到根目录下的 config.yaml
    with open(config_path, "r") as f:
        return yaml.safe_load(f)  # 使用 safe_load 避免潜在的安全问题


# 实例化配置对象
config = load_config()
