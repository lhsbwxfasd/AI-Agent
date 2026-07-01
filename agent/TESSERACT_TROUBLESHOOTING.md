# Tesseract OCR Windows 故障排查指南

## 问题现象

```
WARNING - OCR failed: tesseract is not installed or it's not in your PATH
```

即使已安装 Tesseract 并添加到 PATH，Python 仍然找不到。

## 原因分析

### 1. 环境变量未生效
- **原因**：修改环境变量后，已运行的进程不会自动更新
- **解决**：重启命令行窗口或重启 Python 进程

### 2. Python 进程隔离
- **原因**：Python 子进程可能使用不同的环境
- **解决**：在代码中显式设置路径

### 3. PATH 格式问题
- **原因**：PATH 中路径格式不正确
- **解决**：检查 PATH 格式，确保没有多余空格或分号

## 解决方案

### 方案1：运行验证脚本（推荐）

```bash
cd agent
python verify_tesseract.py
```

这个脚本会：
- ✅ 检查系统环境变量
- ✅ 查找 Tesseract 安装路径
- ✅ 测试 Python 集成
- ✅ 执行 OCR 功能测试

### 方案2：运行快速配置工具

```bash
cd agent
setup_tesseract.bat
```

自动完成配置和验证。

### 方案3：手动验证

#### 步骤1：验证 Tesseract 安装

打开**新的**命令行窗口（重要！）：

```bash
# 检查版本
tesseract --version

# 检查语言包
tesseract --list-langs

# 测试 OCR
echo Hello World | convert -pointsize 20 text:- test.png
tesseract test.png output
type output.txt
```

如果命令找不到，说明：
1. PATH 未正确设置
2. 需要重启命令行窗口
3. 需要重启系统（最彻底）

#### 步骤2：验证 Python 集成

```python
python
>>> import pytesseract
>>> print(pytesseract.get_tesseract_version())
>>> print(pytesseract.get_languages())
>>> exit()
```

#### 步骤3：显式设置路径

在 Python 中手动设置：

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 测试
print(pytesseract.get_tesseract_version())
```

### 方案4：重启后端服务

**最重要的一步！**

```bash
# 停止当前运行的后端（Ctrl+C）

# 重新启动
cd agent
python main.py
```

重启后，代码会自动：
1. 查找 Tesseract 安装路径
2. 设置 pytesseract 路径
3. 验证 OCR 功能
4. 输出初始化日志

查看启动日志，应该看到：

```
INFO - Tesseract OCR path set to: C:\Program Files\Tesseract-OCR\tesseract.exe
INFO - Tesseract OCR initialized successfully, version: 5.3.3
```

## 常见问题

### Q1: tesseract --version 能运行，但 Python 找不到？

**原因**：Python 进程启动时环境变量未更新

**解决**：
```bash
# 方案1：重启后端服务
python main.py

# 方案2：在代码中显式设置（已自动处理）
# 代码已更新，会自动查找路径
```

### Q2: 提示语言包缺失？

**错误**：
```
Failed loading language 'chi_sim'
```

**解决**：
```bash
# 检查语言包
tesseract --list-langs

# 如果缺少中文，重新安装 Tesseract
# 安装时勾选 Chinese (Simplified)
```

### Q3: 权限问题？

**错误**：
```
Permission denied
```

**解决**：
```bash
# 以管理员身份运行
# 右键 -> 以管理员身份运行
```

### Q4: 路径有空格导致问题？

**解决**：
```python
# 使用原始字符串
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 或使用短路径名
pytesseract.pytesseract.tesseract_cmd = 'C:\\PROGRA~1\\Tesseract-OCR\\tesseract.exe'
```

## 完整检查清单

### ✅ 安装检查

- [ ] Tesseract OCR 已安装
- [ ] 安装路径：`C:\Program Files\Tesseract-OCR\`
- [ ] 已安装中文语言包（chi_sim）
- [ ] 已安装英文语言包（eng）

### ✅ 环境变量检查

- [ ] PATH 包含：`C:\Program Files\Tesseract-OCR`
- [ ] 已重启命令行窗口
- [ ] 已重启 Python 进程

### ✅ Python 检查

- [ ] pytesseract 已安装：`pip show pytesseract`
- [ ] Pillow 已安装：`pip show Pillow`
- [ ] Python 版本：3.10+

### ✅ 功能检查

- [ ] `tesseract --version` 正常
- [ ] `tesseract --list-langs` 显示中文
- [ ] Python 可以导入 pytesseract
- [ ] Python 可以获取版本号
- [ ] OCR 测试成功

### ✅ 服务检查

- [ ] 后端服务已重启
- [ ] 启动日志显示 Tesseract 初始化成功
- [ ] 上传图片测试成功

## 测试步骤

### 1. 命令行测试

```bash
# 创建测试图片
echo Test 测试 | convert -pointsize 20 text:- test.png

# 执行 OCR
tesseract test.png output -l chi_sim+eng

# 查看结果
type output.txt

# 清理
del test.png output.txt
```

### 2. Python 测试

```python
import pytesseract
from PIL import Image, ImageDraw

# 设置路径（如果需要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 创建测试图片
img = Image.new('RGB', (200, 50), 'white')
draw = ImageDraw.Draw(img)
draw.text((10, 10), "Hello 你好", fill='black')

# 执行 OCR
text = pytesseract.image_to_string(img, lang='chi_sim+eng')
print(f"OCR 结果: {text}")
```

### 3. 应用测试

```bash
# 启动后端
cd agent
python main.py

# 查看日志，确认：
# INFO - Tesseract OCR initialized successfully

# 启动前端
cd web
npm run dev

# 浏览器访问
http://localhost:3000

# 上传图片，测试 OCR
```

## 代码已自动修复

好消息！代码已更新，会自动：

1. ✅ 检测 Windows 系统
2. ✅ 搜索常见安装路径
3. ✅ 从 PATH 环境变量查找
4. ✅ 显式设置 tesseract_cmd
5. ✅ 验证并输出初始化日志

**只需重启后端服务即可！**

```bash
cd agent
python main.py
```

查看启动日志，应该看到：

```
INFO - Tesseract OCR path set to: C:\Program Files\Tesseract-OCR\tesseract.exe
INFO - Tesseract OCR initialized successfully, version: 5.3.3
```

## 如果仍然失败

### 最后的解决方案

1. **完全重启**：
   ```bash
   # 关闭所有命令行窗口
   # 关闭 Python 进程
   # 重启系统（可选）
   ```

2. **重新安装 Tesseract**：
   - 卸载当前版本
   - 重新下载最新版本
   - 安装时勾选所有语言包
   - 添加到 PATH

3. **使用绝对路径**：
   
   修改 `attachment_service.py`，硬编码路径：
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

4. **查看详细错误**：
   
   在代码中添加调试：
   ```python
   import pytesseract
   print(f"tesseract_cmd: {pytesseract.pytesseract.tesseract_cmd}")
   print(f"PATH: {os.environ.get('PATH')}")
   ```

## 联系支持

如果以上都无法解决，请提供：

1. `tesseract --version` 输出
2. `python verify_tesseract.py` 输出
3. 后端启动日志
4. 错误截图

我会帮你进一步排查！
