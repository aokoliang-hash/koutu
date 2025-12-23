import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide", page_title="kolang 的 AI 智能抠图工具")

st.write("## 🎨 AI 智能抠图工具")
st.write(":dog: 上传一张图片，自动移除背景。如果效果不佳，可以尝试更换抠图模型。")

# --- UI 元素 ---
st.sidebar.write("## 上传与设置")
# 1. 添加模型选择框
model_name = st.sidebar.selectbox(
    "选择抠图模型",
    ("u2net", "isnet-general-use", "u2net_human_seg", "u2netp")
)
st.sidebar.write("---")
my_upload = st.sidebar.file_uploader("请上传图片", type=["png", "jpg", "jpeg"])

# --- 处理逻辑 ---
if my_upload is not None:
    image = Image.open(my_upload)
    
    col1, col2 = st.columns(2)
    with col1:
        st.header("原图")
        st.image(image)

    with st.spinner('AI 正在努力抠图中...'):
        # 2. 使用用户选择的模型
        fixed = remove(image, model_name=model_name)
        
        buf = BytesIO()
        fixed.save(buf, format="PNG")
        byte_im = buf.getvalue()

    with col2:
        st.header("抠图结果")
        st.image(fixed)
        st.download_button(
            label="下载透明背景图片",
            data=byte_im,
            file_name="removed_bg.png",
            mime="image/png"
        )
else:
    st.info("👈 请在左侧上传图片开始使用")

st.sidebar.markdown("---")
st.sidebar.subheader("模型说明:")
st.sidebar.info(
    """
    - **u2net**: 默认通用模型，适合大多数情况。
    - **isnet-general-use**: 高精度通用模型，细节保留更好（推荐）。
    - **u2net_human_seg**: 专门用于人像分割。
    - **u2netp**: 一个轻量级的通用模型。
    """
)
