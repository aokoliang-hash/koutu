import streamlit as st
from rembg import remove, new_session
from PIL import Image
import io
import numpy as np

# --- 页面配置 ---
st.set_page_config(layout="wide", page_title="AI 建筑/通用抠图专业版")

st.markdown("""
<style>
    .stApp {max-width: 100%;}
    img {max-width: 100%;}
</style>
""", unsafe_allow_html=True)

st.write("## 🏙️ kolang 的 AI 智能抠图工具 (专业版)")
st.write("针对建筑、复杂背景优化，支持手动修复“幽灵”半透明问题。")

# --- 侧边栏设置 ---
st.sidebar.header("🛠️ 设置面板")

# 1. 模型选择
st.sidebar.subheader("1. 模型选择")
model_type = st.sidebar.selectbox(
    "推荐尝试不同模型",
    ("isnet-general-use", "isnet-anime", "u2net"),
    index=0,
    help="isnet-general-use: 细节最好；isnet-anime: 对插画/效果图/高对比度图片效果奇佳。"
)

# 2. 高级处理策略
st.sidebar.subheader("2. 修复策略 (关键)")

# 策略 A: Alpha Matting
use_alpha_matting = st.sidebar.checkbox("启用 Alpha Matting (边缘精修)", value=False, help="启用后边缘更柔和，但处理速度变慢。")
if use_alpha_matting:
    fg_threshold = st.sidebar.slider("前景阈值 (Foreground)", 0, 255, 240)
    bg_threshold = st.sidebar.slider("背景阈值 (Background)", 0, 255, 10)
    erode_size = st.sidebar.slider("腐蚀大小 (Erode)", 0, 50, 10)
else:
    fg_threshold = 240
    bg_threshold = 10
    erode_size = 10

st.sidebar.markdown("---")

# 策略 B: 强制不透明 (针对你的问题)
st.sidebar.subheader("3. 后期修正")
force_solid = st.sidebar.checkbox("🧱 强制不透明 (修复半透明建筑)", value=False, help="勾选此项！如果旁边的楼变半透明了，这个功能会强制把它们变回实心。")
solid_threshold = 0
if force_solid:
    solid_threshold = st.sidebar.slider("不透明度识别灵敏度", 1, 200, 30, help="数值越小，识别越灵敏。只要有一点点影子就保留。")


# --- 主逻辑 ---
my_upload = st.sidebar.file_uploader("上传图片 (JPG/PNG)", type=["png", "jpg", "jpeg"])

if my_upload is not None:
    # 加载图片
    image = Image.open(my_upload)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("原始图片")
        st.image(image)

    with st.spinner('AI 正在计算像素... (第一次加载模型需等待)'):
        try:
            # 1. 创建会话
            session = new_session(model_type)
            
            # 2. 执行抠图
            # 注意：这里把 alpha_matting 的参数传进去了
            fixed = remove(
                image, 
                session=session,
                alpha_matting=use_alpha_matting,
                alpha_matting_foreground_threshold=fg_threshold,
                alpha_matting_background_threshold=bg_threshold,
                alpha_matting_erode_size=erode_size
            )

            # 3. [关键步骤] 强制不透明处理
            if force_solid:
                # 把图片转成 numpy 数组方便操作
                img_array = np.array(fixed)
                
                # 获取 Alpha 通道 (第4个通道)
                # 逻辑：如果 Alpha 值大于设定的阈值(比如30)，就直接改成 255 (完全不透明)
                alpha_channel = img_array[:, :, 3]
                mask = alpha_channel > solid_threshold
                img_array[:, :, 3][mask] = 255
                
                # 转回图片对象
                fixed = Image.fromarray(img_array)

            # 4. 展示结果
            with col2:
                st.subheader("抠图结果")
                st.image(fixed)
                
                # 转换下载格式
                buf = io.BytesIO()
                fixed.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 下载结果",
                    data=byte_im,
                    file_name=f"koutu_{model_type}.png",
                    mime="image/png"
                )

        except Exception as e:
            st.error(f"出错啦: {e}")

else:
    st.info("👈 请在左侧上传图片。针对你的建筑图，建议勾选【强制不透明】功能。")
