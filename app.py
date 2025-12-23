import streamlit as st
from rembg import remove, new_session  # <--- 1. 这里多引入了 new_session
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide", page_title="kolang 制作的 AI 智能抠图工具")

st.write("## 🎨 kolang 的 AI 智能抠图工具")
st.write(":dog: 上传一张图片，自动移除背景。如果效果不佳，请尝试切换模型。")

# --- UI 元素 ---
st.sidebar.write("## 上传与设置")

# 模型选择
model_name = st.sidebar.selectbox(
    "选择抠图模型",
    ("u2net", "isnet-general-use", "u2net_human_seg", "u2netp"),
    index=0 # 默认选中第一个
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

    with st.spinner(f'正在使用 {model_name} 模型抠图中...'):
        # --- 2. 修正后的核心代码 ---
        try:
            # 第一步：创建一个 session (会话)，指定要用的模型
            session = new_session(model_name)
            
            # 第二步：将 session 传给 remove 函数
            fixed = remove(image, session=session)
            
            # --- 图片处理完毕 ---
            
            buf = BytesIO()
            fixed.save(buf, format="PNG")
            byte_im = buf.getvalue()

            with col2:
                st.header("抠图结果")
                st.image(fixed)
                st.download_button(
                    label="下载透明背景图片",
                    data=byte_im,
                    file_name=f"removed_bg_{model_name}.png",
                    mime="image/png"
                )
        except Exception as e:
            st.error(f"发生错误: {e}")
            st.warning("提示：如果是第一次使用某个模型，系统需要下载模型文件，可能会超时或失败。请刷新页面重试。")
            
else:
    st.info("👈 请在左侧上传图片开始使用")

st.sidebar.markdown("---")
st.sidebar.subheader("模型说明:")
st.sidebar.info(
    """
    - **u2net**: 默认模型，均衡。
    - **isnet-general-use**: 🔥 推荐！细节处理最好（适合建筑/复杂背景）。
    - **u2net_human_seg**: 专门用于人像。
    - **u2netp**: 轻量版，速度快但精度略低。
    """
)
