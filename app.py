import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

# 设置网页配置
st.set_page_config(layout="wide", page_title="AI 在线抠图工具")

st.write("## 🎨 简易 AI 在线抠图工具")
st.write(":dog: 上传一张图片，自动移除背景 :cat:")

# 创建侧边栏上传组件
st.sidebar.write("## 上传图片")
my_upload = st.sidebar.file_uploader("请上传 JPG 或 PNG 图片", type=["png", "jpg", "jpeg"])

# 处理逻辑
if my_upload is not None:
    # 1. 读取图片
    image = Image.open(my_upload)
    
    # 2. 界面显示：创建两列
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("原图")
        st.image(image)

    # 3. 执行抠图 (第一次运行会自动下载模型，约 100MB+，请耐心等待)
    with st.spinner('正在施展魔法移除背景...'):
        fixed = remove(image)
        
        # 将处理后的图片转换为字节流，以便下载
        buf = BytesIO()
        fixed.save(buf, format="PNG")
        byte_im = buf.getvalue()

    with col2:
        st.header("抠图结果")
        st.image(fixed)
        
        # 4. 提供下载按钮
        st.download_button(
            label="下载透明背景图片",
            data=byte_im,
            file_name="removed_bg.png",
            mime="image/png"
        )
else:
    # 如果没上传，显示示例或提示
    st.info("👈 请在左侧侧边栏上传图片开始使用")
