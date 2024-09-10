# -*- coding: utf-8 -*-

# @version  : python-
# @license  : MIT
# @Software : PyCharm
# @Time     : 2024/8/21 14:58
# @Author   : yzl
# @File     : app.py.py

# @Features : # Enter feature name here
# Enter feature description here
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import pandas as pd
import re
from api import ClsCheckApi

# 创建ClsCheckApi类的实例
api_checker = ClsCheckApi()


# 初始化session state
if 'models' not in st.session_state:
    st.session_state.models = pd.DataFrame({"model": [""]})
if 'success_df' not in st.session_state:
    st.session_state.success_df = pd.DataFrame(columns=["model", "elapsed_time", "selected"])
if 'error_models' not in st.session_state:
    st.session_state.error_models = []

# 创建Streamlit页面布局
st.title("API 模型检查器")

# 输入框（带有默认值）
api_base = st.text_input("输入 API Base")
api_key = st.text_input("输入 API Key")


# 创建两列布局
col1, col2 = st.columns(2)

# 手动输入模型列表
with col1:
    st.subheader("手动输入模型")
    manual_input = st.text_area("手动输入模型列表", help="每行输入一个模型名称, 一行一个, \n 切分", height=150)
    if st.button("添加手动输入的模型"):
        if manual_input:
            # 处理输入的模型名称
            manual_models = [re.sub(r'["\'\\s]', '', model).strip() for model in manual_input.split('\n') if re.sub(r'["\'\\s]', '', model).strip()]
            manual_models = list(set(manual_models))  # 去重
            manual_models.sort()  # 排序

            # 直接用新的模型列表替换现有的模型列表
            st.session_state.models = pd.DataFrame({"model": manual_models})

            # 显示更新成功的消息
            st.success(f"已成功添加 {len(manual_models)} 个模型到列表中。")
        else:
            st.warning("请输入至少一个模型名称")

# 获取模型按钮
with col2:
    st.subheader("自动获取模型")
    st.write("点击下方按钮自动获取模型列表")

    # 添加代理复选框
    api_checker.proxy = st.checkbox("使用代理", help="启用或关闭代理")

    if st.button("自动获取模型", help="自动从 $host/v1/models 获取模型列表"):
        if api_base and api_key:
            api_checker.api_base = api_base
            api_checker.api_key = api_key
            models = api_checker.get_models()
            if len(models) > 0:
                st.session_state.models = pd.DataFrame({"model": models})
                # 显示更新成功的消息
                st.success(f"已成功添加 {len(models)} 个模型到列表中。")
            else:
                st.error(f"未获得有效的模型列表!")
        else:
            st.error("请输入API Base和API Key")

    if st.button("自动填入关心模型"):
        models = api_checker.get_care_modes()
        if len(models) > 0:
            st.session_state.models = pd.DataFrame({"model": models})
            # 显示更新成功的消息
            st.success(f"已成功添加 {len(models)} 个模型到列表中。")
        else:
            st.error(f"未获得有效的模型列表!")


# 模型列表输入（可编辑的DataFrame）
st.subheader("模型列表")

edited_df = st.data_editor(
    st.session_state.models,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "model": st.column_config.TextColumn(
            "Model Name",
            width="large",
            required=True,
        )
    },
    hide_index=False,
)

# 更新session_state中的models
st.session_state.models = edited_df

# 检查模型按钮
if st.button("非流 检查模型"):
    if api_base and api_key and not edited_df.empty and not edited_df['model'].iloc[0] == "":
        api_checker.api_base = api_base
        api_checker.api_key = api_key

        models_to_check = edited_df['model'].tolist()
        total_models = len(models_to_check)

        # 创建进度条
        progress_bar = st.progress(0)

        # 创建用于显示实时结果的容器
        result_container = st.empty()

        success_models = []
        error_models = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_model = {executor.submit(api_checker.check_single_model, model): model for model in models_to_check}

            for i, future in enumerate(as_completed(future_to_model)):
                model = future_to_model[future]

                try:
                    result, elapsed_time = future.result()
                    if result:
                        success_models.append({"model_name": model, "elapsed_time": elapsed_time})
                    else:
                        error_models.append({"model_name": model, "elapsed_time": elapsed_time})
                except Exception as e:
                    error_models.append({"model_name": model, "elapsed_time": 0})

                # 更新进度条
                progress = (i + 1) / total_models
                progress_bar.progress(progress)

                # 更新实时结果
                result_container.markdown(f"""
                ### 检查进度: {i + 1}/{total_models}
                """)

                # 给Streamlit一个机会来更新UI
                st.empty()

        # 清除进度显示
        result_container.empty()

        # 显示最终结果
        st.success("模型检查完成！")

        # 更新session state中的success_df和error_models
        st.session_state.success_df = pd.DataFrame({
            "model": [model["model_name"] for model in success_models],
            "elapsed_time": [model["elapsed_time"] for model in success_models],
            "selected": [True] * len(success_models)  # 默认全选
        })
        st.session_state.error_models = error_models
    else:
        st.error("请确保已输入API Base、API Key，并且至少输入了一个模型")


# 显示可勾选的成功模型列表
st.subheader("成功模型列表")
if not st.session_state.success_df.empty and 'model' in st.session_state.success_df.columns:
    # 添加全选/取消全选复选框
    all_selected = st.checkbox("全选/取消全选", value=True)

    # 根据all_selected的值更新所有行的selected列
    st.session_state.success_df['selected'] = all_selected

    edited_success_df = st.data_editor(
        st.session_state.success_df,
        hide_index=True,
        column_config={
            "model": "模型名称",
            "elapsed_time": st.column_config.NumberColumn("耗时(秒)", format="%.2f"),
            "selected": st.column_config.CheckboxColumn("选择")
        },
        disabled=["model", "elapsed_time"],
        use_container_width=True,
        key="success_df_editor"
    )

    # 更新session state中的success_df，同时处理NaN值
    st.session_state.success_df = edited_success_df.copy()
    st.session_state.success_df['selected'] = st.session_state.success_df['selected'].fillna(False).astype(bool)

    # 根据勾选状态生成拼接字符串
    selected_models = st.session_state.success_df[st.session_state.success_df['selected'] == True]['model'].tolist()
    success_model_names = ",".join(selected_models)

    # 显示成功模型的拼接字符串
    st.subheader("成功模型拼接结果")
    st.text_area(
        label="成功模型拼接结果",
        value=success_model_names,
        height=100,
        help="下面已经按照 ',' 进行拼接, 可以直接贴入 one-api",
    )

    # 显示详细结果
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("成功的模型")

        # 对成功的模型进行排序,选中的排在前面
        sorted_df = st.session_state.success_df.sort_values('selected', ascending=False)

        for _, row in sorted_df.iterrows():
            color = "green" if row['selected'] else "gray"
            st.markdown(f'<p style="color:{color};">{row["model"]} (耗时: {row["elapsed_time"]:.2f}秒)</p>', unsafe_allow_html=True)

    with col2:
        st.subheader("失败的模型")
        for model in st.session_state.error_models:
            st.markdown(f'<p style="color:red;">{model["model_name"]} (耗时: {model["elapsed_time"]:.2f}秒)</p>', unsafe_allow_html=True)
else:
    st.info("还没有成功检查的模型。请先运行模型检查。")
