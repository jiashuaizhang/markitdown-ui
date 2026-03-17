import os
import time
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import streamlit as st
from markitdown import MarkItDown
from markitdown import FileConversionException, UnsupportedFormatException
from markitdown import StreamInfo


@dataclass(frozen=True)
class ConvertOutcome:
    markdown: str
    output_path: Path
    elapsed_s: float


def _derive_output_path(source_path: Path) -> Path:
    return source_path.with_suffix(".md")


def _convert_local_file(source_path: Path) -> ConvertOutcome:
    start = time.perf_counter()
    md = MarkItDown()
    result = md.convert(str(source_path))
    out_path = _derive_output_path(source_path)
    out_path.write_text(result.markdown, encoding="utf-8")
    elapsed = time.perf_counter() - start
    return ConvertOutcome(markdown=result.markdown, output_path=out_path, elapsed_s=elapsed)


def _safe_read_text(path: Path, max_chars: int = 120_000) -> Tuple[str, bool]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ("(无法读取输出文件进行预览)", False)
    if len(text) > max_chars:
        return (text[:max_chars] + "\n\n...(预览已截断)...\n", True)
    return (text, False)


def _is_probably_windows_abs_path(p: str) -> bool:
    if len(p) >= 3 and p[1:3] == ":\\":
        return True
    if p.startswith("\\\\"):
        return True
    return False


st.set_page_config(page_title="MarkItDown UI", layout="centered")
st.title("MarkItDown 简易 UI")
st.caption("输入本机文件路径（推荐）或上传文件，生成同名 .md（默认写回源文件同目录）。")

mode = st.radio(
    "选择输入方式",
    options=["上传文件", "本机路径（同目录输出）"],
    horizontal=True,
    index=0,
)

st.divider()

source_path: Optional[Path] = None
uploaded_bytes: Optional[bytes] = None
uploaded_name: Optional[str] = None
output_dir: Optional[Path] = None

if mode == "本机路径（同目录输出）":
    raw = st.text_input(
        "源文件路径",
        placeholder=r"D:\docs\example.pdf",
        help="必须是当前机器可访问的真实路径；转换结果会写到同目录，后缀改为 .md。",
    ).strip()
    if raw:
        if os.name == "nt" and not _is_probably_windows_abs_path(raw):
            st.warning("看起来不像 Windows 绝对路径；请确认格式，例如：C:\\path\\file.pdf 或 \\\\server\\share\\file.pdf。")
        source_path = Path(raw)
else:
    up = st.file_uploader(
        "上传文件",
        type=None,
        accept_multiple_files=False,
        help="浏览器上传不带原始绝对路径；若你要严格写回源文件同目录，请使用“本机路径（同目录输出）”。",
    )
    out_dir_raw = st.text_input(
        "输出目录（可选）",
        placeholder=r"D:\output",
        help="不填则默认输出到当前工作目录下的 output/；填写则输出到指定目录。输出文件名为同名仅后缀改为 .md。",
    ).strip()

    output_dir = Path(out_dir_raw) if out_dir_raw else (Path.cwd() / "output")

    if up is not None:
        uploaded_bytes = up.getvalue()
        uploaded_name = up.name

st.divider()

col_a, col_b = st.columns([1, 3], vertical_alignment="center")
with col_a:
    do_convert = st.button("开始转换", type="primary", use_container_width=True)
with col_b:
    keep_data_uris = st.checkbox(
        "保留 data URIs（例如 base64 图片）",
        value=True,
        help="默认会截断 data URI；勾选后输出可能更大。",
    )


def _convert_uploaded_file(data: bytes, filename: str, out_dir: Path) -> ConvertOutcome:
    start = time.perf_counter()
    out_dir.mkdir(parents=True, exist_ok=True)

    md = MarkItDown()
    stream = io.BytesIO(data)
    ext = Path(filename).suffix or None
    stream_info = StreamInfo(filename=filename, extension=ext)
    result = md.convert_stream(stream, stream_info=stream_info, keep_data_uris=keep_data_uris)

    out_name = Path(filename).with_suffix(".md").name
    out_path = out_dir / out_name
    out_path.write_text(result.markdown, encoding="utf-8")

    elapsed = time.perf_counter() - start
    return ConvertOutcome(markdown=result.markdown, output_path=out_path, elapsed_s=elapsed)


if do_convert:
    try:
        if mode == "本机路径（同目录输出）":
            if source_path is None:
                st.error("请先输入源文件路径。")
                st.stop()
            if not source_path.exists():
                st.error("文件不存在。")
                st.stop()
            if source_path.is_dir():
                st.error("你输入的是目录，请输入文件路径。")
                st.stop()

            with st.spinner("转换中..."):
                outcome = _convert_local_file(source_path)

        else:
            if uploaded_bytes is None or uploaded_name is None:
                st.error("请先上传文件。")
                st.stop()

            with st.spinner("转换中..."):
                outcome = _convert_uploaded_file(uploaded_bytes, uploaded_name, output_dir)

        st.success(f"完成：写出 `{outcome.output_path}`（耗时 {outcome.elapsed_s:.2f}s）")

        preview_text, truncated = _safe_read_text(outcome.output_path)
        st.subheader("输出预览")
        if truncated:
            st.info("预览内容已截断。")
        st.text_area("Markdown", value=preview_text, height=340)

        st.download_button(
            "下载 .md",
            data=outcome.markdown.encode("utf-8"),
            file_name=outcome.output_path.name,
            mime="text/markdown",
            use_container_width=True,
        )

    except UnsupportedFormatException as e:
        st.error(f"不支持的格式：{e}")
    except FileConversionException as e:
        st.error(f"转换失败：{e}")
    except PermissionError:
        st.error("权限不足：无法读取源文件或写入输出目录。")
    except Exception as e:
        st.error(f"未知错误：{type(e).__name__}: {e}")

