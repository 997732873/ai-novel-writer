import streamlit as st
import openai
from datetime import datetime

# ========== iOS 手机界面适配优化 ==========
st.markdown("""
    <style>
    /* 放大手机端输入框和按钮字体 */
    .stTextInput>div>div>input {font-size: 16px !important; padding: 8px;}
    .stTextArea>div>div>textarea {font-size: 16px !important; line-height: 1.5;}
    .stButton>button {font-size: 16px !important; padding: 10px 20px; width: 100%;}
    .stSelectbox>div>div>select {font-size: 16px !important;}
    /* 优化手机端布局，减少留白 */
    @media (max-width: 768px) {
        .block-container {padding: 10px !important;}
        h1, h2, h3 {font-size: 1.5rem !important;}
    }
    </style>
    """, unsafe_allow_html=True)

# ========== 页面配置 ==========
st.set_page_config(
    page_title="iOS AI小说生成工具",
    page_icon="📖",
    layout="centered"  # 手机端用居中布局更友好
)
st.title("📖 iOS AI小说生成工具")
st.markdown("**玄幻/都市/言情/悬疑 | 支持续写 | 一键导出**")

# ========== 侧边栏配置 ==========
with st.sidebar:
    st.subheader("⚙️ 模型设置")
    model_type = st.radio("选择生成模型", ["GPT-3.5（需API Key）", "免费开源模型（本地部署）"])
    
    if model_type == "GPT-3.5（需API Key）":
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-xxx...")
        openai.api_key = api_key

    st.subheader("📝 风格预设")
    style = st.selectbox(
        "小说风格",
        ["玄幻", "都市", "言情", "悬疑"]
    )

# ========== 风格提示词库（核心） ==========
style_prompt = {
    "玄幻": "东方玄幻风格，语言磅礴大气，包含宗门、修炼境界、法宝、妖兽元素，主角有成长线，情节有爽点，结尾留悬念，符合网文节奏。",
    "都市": "现代都市爽文风格，贴近生活，主角有特殊能力或机遇，包含职场、商战、亲情友情，人物性格鲜明，情节真实不浮夸。",
    "言情": "甜宠言情风格，语言细腻温柔，注重男女主互动和心理描写，情节有甜有小虐，节奏舒缓，适合女性读者，结尾留暧昧伏笔。",
    "悬疑": "悬疑推理风格，语言紧凑简洁，情节环环相扣，伏笔多，反转合理，注重细节描写，营造紧张氛围，结尾留解谜悬念。"
}

# ========== 标签页：新小说生成 + 章节续写 ==========
tab1, tab2 = st.tabs(["📚 新小说生成", "✍️ 章节续写"])

# --- 标签1：新小说生成 ---
with tab1:
    st.subheader("填写小说基础信息")
    novel_name = st.text_input("小说名称", placeholder="如《剑神归来》《都市之全能奶爸》")
    protagonist = st.text_input("主角名字", placeholder="如萧炎、林辰、苏晚")
    core_setting = st.text_area("核心设定（30字内）", placeholder="主角穿越修仙界，获签到系统，开局送神器", height=80)
    
    col1, col2 = st.columns(2)
    with col1:
        chapter_num = st.number_input("章节号", min_value=1, value=1)
    with col2:
        word_count = st.slider("字数", 500, 3000, 1000, step=100)
    
    chapter_title = st.text_input("章节标题", placeholder="如：第一章 青云宗签到，得混沌神剑")
    generate_btn = st.button("🚀 生成章节内容", type="primary")

    if generate_btn:
        if not (novel_name and protagonist and core_setting):
            st.error("请填写小说名称、主角、核心设定！")
        elif model_type == "GPT-3.5（需API Key）" and not api_key:
            st.error("请输入OpenAI API Key！")
        else:
            with st.spinner("AI正在创作..."):
                # 构建Prompt
                prompt = f"""
                请创作小说《{novel_name}》第{chapter_num}章《{chapter_title}》，要求：
                1. 风格：{style_prompt[style]}
                2. 主角：{protagonist}
                3. 核心设定：{core_setting}
                4. 字数：约{word_count}字，结构完整（开头-发展-小高潮），分段合理，符合网文阅读习惯。
                """
                # 调用GPT
                if model_type == "GPT-3.5（需API Key）":
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.8  # 创意度
                        )
                        novel_content = response.choices[0].message.content
                    except Exception as e:
                        novel_content = f"生成失败：{str(e)}"
                else:
                    novel_content = "【免费开源模型需本地部署】请参考教程部署ChatGLM后使用"
                
                # 显示结果 + 导出
                st.subheader(f"《{novel_name}》第{chapter_num}章")
                st.write(novel_content)

                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                file_name = f"{novel_name}_第{chapter_num}章_{timestamp}.txt"
                st.download_button(
                    label="📥 导出TXT",
                    data=novel_content,
                    file_name=file_name,
                    mime="text/plain"
                )

# --- 标签2：章节续写 ---
with tab2:
    st.subheader("粘贴上一章内容（或片段）")
    last_chapter = st.text_area("上一章内容", height=150, placeholder="粘贴结尾部分，AI自动衔接情节...")
    continue_req = st.text_input("续写要求", placeholder="主角遇强敌反杀/女主误会主角/揭开伏笔...")
    continue_btn = st.button("✍️ 开始续写", type="primary")

    if continue_btn:
        if not last_chapter:
            st.error("请粘贴需要续写的内容！")
        elif model_type == "GPT-3.5（需API Key）" and not api_key:
            st.error("请输入OpenAI API Key！")
        else:
            with st.spinner("AI正在续写..."):
                prompt = f"""
                请续写以下小说内容，要求：
                1. 风格：{style_prompt[style]}
                2. 上一章内容：{last_chapter}
                3. 续写要求：{continue_req}
                4. 衔接自然，保持人物性格一致，字数约500字，结尾留悬念。
                """
                if model_type == "GPT-3.5（需API Key）":
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.8
                        )
                        continue_content = response.choices[0].message.content
                    except Exception as e:
                        continue_content = f"续写失败：{str(e)}"
                else:
                    continue_content = "【免费开源模型需本地部署】"
                
                st.subheader("续写内容")
                st.write(continue_content)
                st.download_button(
                    label="📥 导出续写内容",
                    data=continue_content,
                    file_name=f"小说续写_{datetime.now().strftime('%Y%m%d%H%M')}.txt",
                    mime="text/plain"
                )

# ========== 提示 ==========
st.markdown("---")
st.warning("⚠️ 提示：生成内容仅供参考，遵守法律法规，勿用于商业用途！")
