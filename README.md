# MarkItDown Streamlit UI

一个极简的本地 UI：选择/指定文件 → 调用 `markitdown` 转换 → 生成同名 `.md` 输出文件。

## 环境准备

本项目目录本身就是一个 venv（你已在其中安装了 `markitdown`）。需要额外安装 `streamlit`：

```powershell
.\Scripts\activate
pip install -r requirements.txt
```

## 启动

```powershell
.\Scripts\activate
python -m streamlit run app.py
```

启动后在浏览器打开 Streamlit 提示的地址即可。

## 使用方式

页面提供两种输入模式：

- **本机路径（推荐）**：输入本机可访问的源文件绝对路径（如 `D:\docs\example.pdf`），点击“开始转换”，会在源文件同目录生成 `example.md`。
- **上传文件**：浏览器上传无法携带原始路径，因此需要你额外填写一个“输出目录”。转换后会在该目录下生成同名 `.md`。

## 常见问题

- **输出路径/覆盖**：输出文件名固定为“同名仅后缀改为 `.md`”。若已存在同名 `.md`，会被覆盖。
- **权限问题**：如果源文件目录无写权限，会提示权限不足；请换到可写目录或以有权限的目录作为输出。
- **格式不支持**：`markitdown` 对部分格式可能不支持，会在页面显示“不支持的格式/转换失败”。

