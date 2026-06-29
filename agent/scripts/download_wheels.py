"""
自动下载预编译 wheel 文件
"""
import urllib.request
import os
from pathlib import Path

# 预编译 wheel 文件下载链接
WHEELS = {
    "duckdb": {
        "url": "https://files.pythonhosted.org/packages/65/4b/5e9a8c0a3c8b9a7c0f5e3d5c5b5a5c5e/duckdb-0.9.1-cp38-cp38-win_amd64.whl",
        "filename": "duckdb-0.9.1-cp38-cp38-win_amd64.whl",
        "backup_url": "https://pypi.org/packages/py3/d/duckdb/duckdb-0.9.1-cp38-cp38-win_amd64.whl"
    },
    "hnswlib": {
        "url": "https://files.pythonhosted.org/packages/c9/52/92/b4b22fa3e652073584067109b5094dbd5c73b42738e41213f6/hnswlib-0.8.0-cp38-cp38-win_amd64.whl",
        "filename": "hnswlib-0.8.0-cp38-cp38-win_amd64.whl",
        "backup_url": "https://pypi.org/packages/py3/h/hnswlib/hnswlib-0.8.0-cp38-cp38-win_amd64.whl"
    }
}

def download_file(url: str, filepath: Path) -> bool:
    """下载文件"""
    try:
        print(f"正在下载: {url}")
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ 下载成功: {filepath.name}")
        return True
    except Exception as e:
        print(f"✗ 下载失败: {str(e)}")
        return False

def main():
    """主函数"""
    # 创建 wheels 目录
    wheels_dir = Path(__file__).parent.parent / "wheels"
    wheels_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("预编译 Wheel 文件下载工具")
    print("=" * 60)
    print(f"下载目录: {wheels_dir}\n")
    
    downloaded = []
    failed = []
    
    for name, info in WHEELS.items():
        filepath = wheels_dir / info["filename"]
        
        # 如果文件已存在，跳过
        if filepath.exists():
            print(f"✓ 文件已存在: {info['filename']}")
            downloaded.append(name)
            continue
        
        # 尝试主链接
        if download_file(info["url"], filepath):
            downloaded.append(name)
        else:
            # 尝试备用链接
            print(f"尝试备用链接...")
            if download_file(info["backup_url"], filepath):
                downloaded.append(name)
            else:
                failed.append(name)
        
        print()
    
    print("=" * 60)
    print(f"下载完成: {len(downloaded)}/{len(WHEELS)}")
    
    if failed:
        print(f"\n失败的包: {', '.join(failed)}")
        print("\n请手动下载:")
        for name in failed:
            info = WHEELS[name]
            print(f"  {name}: {info['backup_url']}")
        return False
    else:
        print("\n✓ 所有文件下载成功！")
        print("\n下一步:")
        print("  1. python -m pip install wheels\\duckdb-0.9.1-cp38-cp38-win_amd64.whl")
        print("  2. python -m pip install wheels\\hnswlib-0.8.0-cp38-cp38-win_amd64.whl")
        print("  3. python -m pip install -r requirements.txt")
        return True

if __name__ == "__main__":
    main()
