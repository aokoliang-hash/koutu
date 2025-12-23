import streamlit as st
from rembg import remove, new_session
from PIL import Image
import io
import numpy as np

# --- 页面配置 ---
st.set_page_config(layout="wide", page_title="AI 智能抠图工具 (轻量版)")

st.write("## 🎨 kolang AI 智能抠图工具")
st.warning("⚠️ 注意：Streamlit 免费服务器内存有限(1GB)。如果使用 'isnet' 模型导致崩溃，请切换回 'u2net' 或 'u2netp'。")

# --- 侧边栏设置 ---
st.sidebar.header("🛠️ 设置面板")

# 1. 模型选择 (修改：默认改为 u2net，更稳定)
model_type = st.sidebar.selectbox(
    "选择模型 (推荐 u2net)",
    ("isnet-general-use", "isnet-anime", "u2net", "u2netp"),
    index=2, # <--- 改为默认选中 u2net，防止上来就崩
    help="u2net: 平衡；u2netp: 最快(省内存)；isnet: 效果最好但容易内存溢出。"
)

# 2. 高级处理策略
st.sidebar.subheader("2. 修复策略")
use_alpha_matting = st.sidebar.checkbox("启用边缘精修 (耗内存)", value=False, help="慎点！可能导致免费服务器崩溃。")

if use_alpha_matting:
    fg_threshold = st.sidebar.slider("前景阈值", 0, 255, 240)
    bg_threshold = st.sidebar.slider("背景阈值", 0, 255, 10)
    erode_size = st.sidebar.slider("腐蚀大小", 0, 50, 10)
else:
    fg_threshold = 240
    bg_threshold = 10
    erode_size = 10

st.sidebar.markdown("---")
# 强制不透明
force_solid = st.sidebar.checkbox("🧱 强制不透明 (修复半透明)", value=False)
solid_threshold = st.sidebar.slider("不透明度识别灵敏度", 1, 200, 30) if force_solid else 30

# --- 主逻辑 ---
my_upload = st.sidebar.file_uploader("上传图片", type=["png", "jpg", "jpeg"])

if my_upload is not None:
    image = Image.open(my_upload)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("原图")
        st.image(image)

    with st.spinner(f'正在使用 {model_type} 计算...'):
        try:
            # 1. 创建会话
            session = new_session(model_type)
            
            # 2. 执行抠图
            fixed = remove(
                image, 
                session=session,
                alpha_matting=use_alpha_matting,
                alpha_matting_foreground_threshold=fg_threshold,
                alpha_matting_background_threshold=bg_threshold,
                alpha_matting_erode_size=erode_size
            )

            # 3. 强制不透明处理
            if force_solid:
                img_array = np.array(fixed)
                # 兼容性处理：确保是 RGBA 模式
                if img_array.shape[2] == 4:
                    alpha_channel = img_array[:, :, 3]
                    mask = alpha_channel > solid_threshold
                    img_array[:, :, 3][mask] = 255
                    fixed = Image.fromarray(img_array)

            with col2:
                st.subheader("结果")
                st.image(fixed)
                
                buf = io.BytesIO()
                fixed.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button("📥 下载图片", byte_im, f"result_{model_type}.png", "image/png")

        except Exception as e:
            st.error(f"发生错误: {e}")
            st.info("💡 提示：如果是内存溢出(MemoryError)，请尝试切换到 'u2netp' 模型，或关闭边缘精修。")

else:
    st.info("👈 请上传图片")
