# simple-plt-webui
一个输入数据绘图的简单工具, 绘图基于Matplotlib, 前端使用Streamlit, 也包括了一些`NumPy`和`SciPy`的简单数据处理功能。

---

## 使用方法
### 安装依赖项
确保电脑上已安装Python (原测试采用的是Python 3.13.9) 。建议使用虚拟环境工具，如uv:
```powershell
winget install python.python.3.13 uv
```
进入`app.py`所在目录，运行以下命令以启用虚拟环境:
```powershell
uv python pin 3.13
uv venv
```
安装依赖:
```powershell
uv pip install -r requirements.txt
```
### 启动应用
激活虚拟环境:
```powershell
.venv/Scripts/Activate.ps1
```
启动webui:
```powershell
python -m streamlit run app.py
```
默认会在 http://localhost:8501/ 打开应用界面。

---
## Todo
- [ ] 前后端分离
- [ ] 增加更多二维曲线图以外的功能