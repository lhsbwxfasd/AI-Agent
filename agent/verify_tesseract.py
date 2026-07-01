"""
Tesseract OCR 验证脚本
用于检查 Tesseract OCR 是否正确安装和配置
"""

import os
import sys

print("=" * 60)
print("Tesseract OCR 验证工具")
print("=" * 60)
print()

# 1. 检查系统环境变量
print("【1】检查系统环境变量")
print("-" * 60)
path_env = os.environ.get('PATH', '')
print(f"PATH 环境变量长度: {len(path_env)} 字符")

tesseract_in_path = False
for path_dir in path_env.split(os.pathsep):
    if 'tesseract' in path_dir.lower():
        print(f"✅ 在 PATH 中找到: {path_dir}")
        tesseract_in_path = True

if not tesseract_in_path:
    print("❌ PATH 中未找到 Tesseract 相关路径")
print()

# 2. 检查常见安装路径
print("【2】检查常见安装路径")
print("-" * 60)

common_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Tesseract-OCR\tesseract.exe',
]

tesseract_exe = None
for path in common_paths:
    if os.path.exists(path):
        print(f"✅ 找到 Tesseract: {path}")
        tesseract_exe = path
        break
    else:
        print(f"❌ 不存在: {path}")

if not tesseract_exe:
    # 尝试在 PATH 中查找
    for path_dir in path_env.split(os.pathsep):
        exe_path = os.path.join(path_dir, 'tesseract.exe')
        if os.path.exists(exe_path):
            print(f"✅ 在 PATH 中找到: {exe_path}")
            tesseract_exe = exe_path
            break

print()

# 3. 测试 pytesseract
print("【3】测试 Python pytesseract 库")
print("-" * 60)

try:
    import pytesseract
    print("✅ pytesseract 库已安装")
    
    # 设置路径
    if tesseract_exe:
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe
        print(f"✅ 已设置 tesseract_cmd: {tesseract_exe}")
    
    # 获取版本
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract 版本: {version}")
    except Exception as e:
        print(f"❌ 获取版本失败: {e}")
    
    # 获取语言包
    try:
        langs = pytesseract.get_languages()
        print(f"✅ 已安装语言包: {', '.join(langs)}")
        
        if 'chi_sim' in langs:
            print("   ✅ 简体中文 (chi_sim) 已安装")
        else:
            print("   ❌ 简体中文 (chi_sim) 未安装")
            
        if 'eng' in langs:
            print("   ✅ 英文 (eng) 已安装")
        else:
            print("   ❌ 英文 (eng) 未安装")
    except Exception as e:
        print(f"❌ 获取语言包失败: {e}")
        
except ImportError as e:
    print(f"❌ pytesseract 未安装: {e}")
    print("   解决方案: pip install pytesseract")

print()

# 4. 测试 Pillow
print("【4】测试 Pillow 库")
print("-" * 60)

try:
    from PIL import Image
    print("✅ Pillow 库已安装")
except ImportError as e:
    print(f"❌ Pillow 未安装: {e}")
    print("   解决方案: pip install Pillow")

print()

# 5. 创建测试图片并执行 OCR
print("【5】OCR 功能测试")
print("-" * 60)

if tesseract_exe:
    try:
        from PIL import Image, ImageDraw, ImageFont
        import pytesseract
        
        # 创建测试图片
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # 使用默认字体
        try:
            draw.text((10, 10), "Hello 你好 Test 测试", fill='black')
        except:
            draw.text((10, 10), "Hello Test", fill='black')
        
        test_img_path = "test_ocr.png"
        img.save(test_img_path)
        print(f"✅ 创建测试图片: {test_img_path}")
        
        # 执行 OCR
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        
        print(f"✅ OCR 识别结果: {text.strip()}")
        print("✅ OCR 功能测试成功！")
        
        # 清理
        os.remove(test_img_path)
        
    except Exception as e:
        print(f"❌ OCR 测试失败: {e}")
else:
    print("⚠️ 跳过 OCR 测试（未找到 Tesseract）")

print()

# 6. 总结和建议
print("=" * 60)
print("验证总结")
print("=" * 60)

if tesseract_exe:
    print("✅ Tesseract OCR 已正确安装")
    print(f"   路径: {tesseract_exe}")
    print()
    print("下一步:")
    print("1. 重启后端服务: python main.py")
    print("2. 上传图片测试 OCR 功能")
else:
    print("❌ Tesseract OCR 未找到")
    print()
    print("解决方案:")
    print("1. 下载安装: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. 安装时勾选中文语言包")
    print("3. 添加到系统 PATH: C:\\Program Files\\Tesseract-OCR")
    print("4. 重启命令行窗口")
    print("5. 重新运行此验证脚本")

print()
print("=" * 60)

# 暂停（Windows）
if os.name == 'nt':
    input("按 Enter 键退出...")
