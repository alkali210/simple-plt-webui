import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from plot_type import draw_plot_content
from code_generator import generate_plot_code

# 设置页面配置
st.set_page_config(
    page_title="Simple plt WebUI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS以实现更现代的Material/Fluent风格
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #0078d4;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #106ebe;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化Session State
if 'df' not in st.session_state:
    # 生成一些默认的示例数据
    data = {
        'Time (s)': np.linspace(0, 10, 20),
        'Voltage (V)': np.sin(np.linspace(0, 10, 20)) + np.random.normal(0, 0.1, 20),
        'Current (A)': np.cos(np.linspace(0, 10, 20)) * 0.5 + np.random.normal(0, 0.05, 20),
        'Temperature (C)': np.linspace(20, 100, 20) + np.random.normal(0, 2, 20)
    }
    st.session_state.df = pd.DataFrame(data)

# 侧边栏 - 控制面板
with st.sidebar:
    st.title("设置")
    
    # 1. 数据操作 (保持展开)
    with st.expander("数据操作", expanded=True):
        # 新增：编码选择，解决中文乱码问题
        encoding = st.selectbox("文件编码 (仅CSV有效)", ["utf-8", "gbk", "gb18030", "cp936", "latin1"], index=0)
        
        uploaded_file = st.file_uploader("导入 CSV/Excel", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    st.session_state.df = pd.read_csv(uploaded_file, encoding=encoding)
                else:
                    st.session_state.df = pd.read_excel(uploaded_file)
                st.success("数据加载成功!")
            except Exception as e:
                st.error(f"加载失败: {e}")
        
        if st.button("重置示例数据"):
            data = {
                'Time (s)': np.linspace(0, 10, 20),
                'Voltage (V)': np.sin(np.linspace(0, 10, 20)) + np.random.normal(0, 0.1, 20),
                'Current (A)': np.cos(np.linspace(0, 10, 20)) * 0.5 + np.random.normal(0, 0.05, 20),
                'Temperature (C)': np.linspace(20, 100, 20) + np.random.normal(0, 2, 20)
            }
            st.session_state.df = pd.DataFrame(data)
            st.rerun()

    # 2. 基础绘图设置 (保持展开)
    with st.expander("基础设置", expanded=True):
        plot_type = st.selectbox(
            "图表类型",
            [
                "Line Plot (折线图)", 
                "Scatter Plot (散点图)", 
                "Bar Chart (柱状图)", 
                "Histogram (直方图)", 
                "Box Plot (箱线图)", 
                "Pie Chart (饼图)",
                "Area Chart (面积图)",
                "Violin Plot (小提琴图)",
                "Correlation Heatmap (相关性热力图)"
            ],
            index=0
        )
        
        # 根据图表类型动态显示列选择
        cols = st.session_state.df.columns.tolist()
        
        # 初始化变量以避免 UnboundLocalError
        bins = 20
        legend_loc = 'best'
        interp_kind = 'linear'
        interp_factor = 5
        peak_prominence = 0.1
        peak_width = 0.0
        extra_axes = []
        
        match plot_type:
            case "Histogram (直方图)":
                x_col = st.selectbox("目标数据列", cols, index=1)
                y_cols = [] # 直方图不需要Y轴选择
                bins = st.slider("分箱数量 (Bins)", 5, 100, 20)
            case "Pie Chart (饼图)":
                x_col = st.selectbox("分类标签列 (Labels)", cols, index=0)
                y_col_pie = st.selectbox("数值列 (Values)", cols, index=1)
                y_cols = [y_col_pie] # 饼图只用一个数值列
            case "Box Plot (箱线图)" | "Violin Plot (小提琴图)":
                x_col = None # 箱线图/小提琴图通常不需要X轴列，或者X轴是分组
                y_cols = st.multiselect("数据列 (可多选)", cols, default=[cols[1]] if len(cols) > 1 else [])
            case "Correlation Heatmap (相关性热力图)":
                x_col = None
                y_cols = []
                st.info("热力图将自动计算所有数值列的相关性矩阵。")
            case _ :
                x_col = st.selectbox("X 轴数据", cols, index=0)
                y_cols = st.multiselect("Y 轴数据 (可多选)", cols, default=[cols[1]] if len(cols) > 1 else [])

    # 3. 高级配置 (弹出式)
    # 使用 st.popover 创建弹出式菜单，节省侧边栏空间
    with st.popover("详细配置…", width='stretch'):
        cfg_tab1, cfg_tab2, cfg_tab3, cfg_tab4 = st.tabs(["样式", "axis", "rcParams", "SciPy"])
        
        # --- Tab 1: 样式美化 ---
        with cfg_tab1:
            st.caption(r"$\LaTeX$公式使用``$``包裹，示例: ``$E=mc^2$``")
            plot_title = st.text_input("图表标题", "Experiment Results")
            x_label = st.text_input("X 轴标签", x_col if plot_type != "Histogram (直方图)" else "Value")
            y_label = st.text_input("Y 轴标签", "Value" if plot_type != "Histogram (直方图)" else "Count")
            
            col_grid, col_legend = st.columns(2)
            with col_grid:
                show_grid = st.checkbox("显示网格", True)
            with col_legend:
                show_legend = st.checkbox("显示图例", True)
                
            if show_legend:
                legend_loc = st.selectbox("图例位置", 
                    ["best", "upper right", "upper left", "lower left", "lower right", "center", "center left", "center right", "upper center", "lower center"],
                    index=0
                )
                
            # 样式映射
            ls_map = {"实线 (-)": '-', "虚线 (--)": '--', "点划线 (-.)": '-.', "点线 (:)": ':', "无线条": ''}
            marker_map = {"圆点 (o)": 'o', "方块 (s)": 's', "三角形 (^)": '^', "叉号 (x)": 'x', "无标记": ''}
            
            line_style_val = '-'
            marker_style_val = 'o'
            line_width = 1.5
            marker_size = 50
            alpha = 0.8

            if plot_type in ["Line Plot (折线图)", "Scatter Plot (散点图)", "Box Plot (箱线图)", "Area Chart (面积图)", "Violin Plot (小提琴图)"]:
                st.markdown("---")
                st.markdown("**线条与标记**")
                col_style, col_width = st.columns(2)
                with col_style:
                    ls_label = st.selectbox("线条样式", list(ls_map.keys()), index=0)
                    ms_label = st.selectbox("标记样式", list(marker_map.keys()), index=0)
                    line_style_val = ls_map[ls_label]
                    marker_style_val = marker_map[ms_label]
                with col_width:
                    line_width = st.slider("线条宽度", 0.5, 10.0, 1.5)
                    marker_size = st.slider("标记大小", 10, 200, 50)
                
                alpha = st.slider("不透明度 (Alpha)", 0.1, 1.0, 0.8)
            
            theme_style = st.selectbox("Matplotlib 风格", plt.style.available, index=plt.style.available.index('seaborn-v0_8-whitegrid') if 'seaborn-v0_8-whitegrid' in plt.style.available else 0)

        # --- Tab 2: 坐标轴设置 ---
        with cfg_tab2:
            col_log_x, col_log_y = st.columns(2)
            with col_log_x:
                log_x = st.checkbox("X 轴对数刻度 (Log)", False)
                invert_x = st.checkbox("反转 X 轴", False)
            with col_log_y:
                log_y = st.checkbox("Y 轴对数刻度 (Log)", False)
                invert_y = st.checkbox("反转 Y 轴", False)
                
            st.markdown("**坐标轴范围 (留空自动)**")
            col_xlim_min, col_xlim_max = st.columns(2)
            with col_xlim_min:
                x_min = st.text_input("X Min", "")
            with col_xlim_max:
                x_max = st.text_input("X Max", "")
                
            col_ylim_min, col_ylim_max = st.columns(2)
            with col_ylim_min:
                y_min = st.text_input("Y Min", "")
            with col_ylim_max:
                y_max = st.text_input("Y Max", "")

            # 多坐标轴配置 (仅限折线图/散点图)
            if plot_type in ["Line Plot (折线图)", "Scatter Plot (散点图)"]:
                st.markdown("---")
                st.markdown("**多坐标轴配置 (Multi-Axis)**")
                enable_multiaxis = st.checkbox("启用多坐标轴", False)
                if enable_multiaxis:
                    st.caption("添加额外的Y轴。请注意，多坐标轴模式下，图例可能需要调整位置。")
                    
                    # Axis 2
                    st.markdown("#### 坐标轴 2 (Axis 2)")
                    y_cols_2 = st.multiselect("数据列 (Axis 2)", cols, key="y_cols_2")
                    if y_cols_2:
                        c1, c2, c3 = st.columns([1, 1, 2])
                        with c1:
                            ax2_pos = st.selectbox("位置", ["Right", "Left"], index=0, key="ax2_pos")
                        with c2:
                            ax2_offset = st.number_input("偏移 (Offset)", value=0, step=10, key="ax2_offset")
                        with c3:
                            ax2_label = st.text_input("轴标签", value="Axis 2", key="ax2_label")
                        
                        extra_axes.append({
                            "cols": y_cols_2,
                            "position": ax2_pos.lower(),
                            "offset": ax2_offset,
                            "label": ax2_label
                        })
                    
                    st.markdown("---")
                    # Axis 3
                    st.markdown("#### 坐标轴 3 (Axis 3)")
                    y_cols_3 = st.multiselect("数据列 (Axis 3)", cols, key="y_cols_3")
                    if y_cols_3:
                        c1, c2, c3 = st.columns([1, 1, 2])
                        with c1:
                            ax3_pos = st.selectbox("位置", ["Right", "Left"], index=0, key="ax3_pos")
                        with c2:
                            ax3_offset = st.number_input("偏移 (Offset)", value=60, step=10, key="ax3_offset")
                        with c3:
                            ax3_label = st.text_input("轴标签", value="Axis 3", key="ax3_label")
                        
                        extra_axes.append({
                            "cols": y_cols_3,
                            "position": ax3_pos.lower(),
                            "offset": ax3_offset,
                            "label": ax3_label
                        })

        # --- Tab 3: 全局参数 ---
        with cfg_tab3:
            col_font, col_size = st.columns(2)
            with col_font:
                # 常用中文字体: SimHei (黑体), Microsoft YaHei (微软雅黑), SimSun (宋体)
                font_family = st.text_input("字体 (Font Family)", "SimHei", help="输入系统已安装的字体名称，例如 SimHei 支持中文")
            with col_size:
                font_size = st.number_input("基础字号", 8, 30, 12)
                
            col_w, col_h = st.columns(2)
            with col_w:
                fig_width = st.number_input("图片宽度 (inch)", 4, 30, 10)
            with col_h:
                fig_height = st.number_input("图片高度 (inch)", 3, 20, 6)
                
            dpi = st.slider("分辨率 (DPI)", 72, 1000, 100)
            
            st.markdown("---")
            custom_rc = st.text_area("自定义 (JSON)", placeholder='{"lines.linewidth": 2, "axes.grid": true}')

        # --- Tab 4: SciPy 功能 ---
        with cfg_tab4:
            st.markdown("**interpolation**")
            enable_interp = st.checkbox("启用平滑", False, help="仅对折线图/散点图有效")
            if enable_interp:
                interp_kind = st.selectbox("插值方法", ["linear", "nearest", "zero", "slinear", "quadratic", "cubic", "spline"], index=6)
                interp_factor = st.slider("平滑倍数", 2, 10, 5)
            
            st.markdown("---")
            st.markdown("**find_peaks**")
            enable_peaks = st.checkbox("启用寻峰标记", False, help="仅对折线图有效")
            if enable_peaks:
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    peak_prominence = st.number_input("prominence", value=0.1)
                with col_p2:
                    peak_width = st.number_input("width", value=0.0)
            
            st.markdown("---")
            st.markdown("**Linear Regression**")
            enable_linreg = st.checkbox("启用线性回归", False, help="仅对折线图/散点图有效")
            
            # 初始化回归显示选项，避免 UnboundLocalError
            show_linreg_eq = True
            show_linreg_r2 = True
            show_linreg_p_value = False
            show_linreg_str_err = False
            
            if enable_linreg:
                show_linreg_eq = st.checkbox("显示回归方程", True)
                show_linreg_r2 = st.checkbox("显示R²", True)
                show_linreg_p_value = st.checkbox("显示显著性水平", False)
                show_linreg_str_err = st.checkbox("显示标准误差", False)

# 主界面
st.markdown("一个输入数据并绘图的简单工具, *几乎只能*用于作二维曲线图, 绘图基于[Matplotlib](https://matplotlib.org/), 也包括了一些`NumPy`和`SciPy`的简单数据处理功能。")
st.markdown("[Repository](https://github.com/alkali210/simple-plt-webui)")

# 使用 Tabs 分离数据视图和绘图视图
tab1, tab2, tab3 = st.tabs(["数据表", "绘图预览", "展示代码"])

with tab1:
    col_header, col_toggle = st.columns([3, 1])
    with col_header:
        st.markdown("### 数据表")
    with col_toggle:
        analysis_mode = st.toggle("统计", value=False, help="开启后可选中单元格查看统计信息，但无法编辑数据")

    if analysis_mode:
        st.caption("点击行号选择行，点击列标题选择列")
        
        # 使用 st.dataframe 启用选择功能
        selection = st.dataframe(
            st.session_state.df,
            width='stretch',
            height=400,
            on_select="rerun",
            selection_mode=["multi-row", "multi-column"]
        )
        
        # 默认显示全表统计
        total_rows, total_cols = st.session_state.df.shape
        
        # 计算选中统计
        # st.dataframe 返回包含 selection 属性的对象
        selected_rows = selection.selection.rows
        selected_cols = selection.selection.columns
        
        has_selection = len(selected_rows) > 0 or len(selected_cols) > 0
        
        if has_selection:
            try:
                # 确定行索引
                if len(selected_rows) > 0:
                    target_rows = selected_rows
                else:
                    target_rows = range(total_rows) # 如果没选行，默认所有行 (当选了列时)
                    
                # 确定列名
                if len(selected_cols) > 0:
                    target_cols = selected_cols
                else:
                    target_cols = st.session_state.df.columns.tolist() # 如果没选列，默认所有列 (当选了行时)
                
                subset = st.session_state.df.iloc[target_rows][target_cols]
                
                sel_rows_count = len(target_rows)
                sel_cols_count = len(target_cols)
                sel_items = subset.size
                sel_empty = subset.isna().sum().sum()
                
                # 数值统计
                numeric_subset = subset.select_dtypes(include=[np.number])
                vals = np.array([])
                if not numeric_subset.empty:
                    # flatten to calculate global mean/sum of selection
                    vals = numeric_subset.values.flatten()
                    vals = vals[~np.isnan(vals)]
                
                # 展示
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("选中", f"{sel_rows_count}行, {sel_cols_count}列")
                m2.metric("总项/空值", f"{sel_items} / {sel_empty}")
                
                if len(vals) > 0:
                    m3.metric("求和 (Sum)", f"= {vals.sum():.2f}")
                    m4.metric("均值 (Mean)", f"= {vals.mean():.2f}")
                    
                    s1, s2, s3, s4 = st.columns(4)
                    s1.metric("中位数 (Median)", f"= {np.median(vals):.2f}")
                    s2.metric("方差 (Var)", f"= {np.var(vals):.2f}")
                    s3.metric("最小值 (Min)", f"= {np.min(vals):.2f}")
                    s4.metric("最大值 (Max)", f"= {np.max(vals):.2f}")
                else:
                    m3.metric("求和 (Sum)", "N/A")
                    m4.metric("均值 (Mean)", "N/A")
                    
            except Exception as e:
                st.warning(f"{e} 请选择有效的数据区域进行统计")
        else:
            st.info("请在表格中选择数据以查看详细统计。")
            
        # 始终显示全表统计
        st.caption(f"{total_rows} 行, {total_cols} 列")

    else:
        st.markdown("您可以直接在下方表格中编辑数据，图表将自动更新。")
        
        # 可编辑的 DataFrame
        edited_df = st.data_editor(
            st.session_state.df,
            num_rows="dynamic",
            width='stretch',
            height=500
        )
        
        # 更新 session state
        if not edited_df.equals(st.session_state.df):
            st.session_state.df = edited_df
            st.rerun()
            
        # 编辑模式下也显示全表统计
        total_rows, total_cols = st.session_state.df.shape
        st.caption(f"{total_rows} 行, {total_cols} 列")

with tab2:
    st.markdown("### 绘图预览")
    df_plot = st.session_state.df
    # st.caption("右键点击图片可以下载")

    if len(df_plot) > 0:
        # 创建 Matplotlib 图形
        try:
            # 应用样式和全局设置
            plt.style.use(theme_style)
            plt.rcParams.update({
                'font.sans-serif': [font_family, 'Microsoft YaHei', 'SimHei', 'Arial', 'sans-serif'],
                'axes.unicode_minus': False,
                'font.size': font_size,
                'figure.dpi': dpi
            })
            
            if custom_rc:
                import json
                try:
                    plt.rcParams.update(json.loads(custom_rc))
                except Exception as e:
                    st.warning(f"自定义 rcParams 解析失败: {e}")

            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
            
            # 准备参数，处理可能未定义的变量
            current_bins = bins if 'bins' in locals() else 20
            current_interp_kind = interp_kind if 'interp_kind' in locals() else 'linear'
            current_interp_factor = interp_factor if 'interp_factor' in locals() else 5
            current_peak_prominence = peak_prominence if 'peak_prominence' in locals() else 0.1
            current_peak_width = peak_width if 'peak_width' in locals() else 0.0
            
            draw_plot_content(ax, plot_type, df_plot, x_col, y_cols, 
                              marker_style_val, line_style_val, line_width, marker_size, alpha, font_size,
                              bins=current_bins, 
                              enable_interp=enable_interp, interp_kind=current_interp_kind, interp_factor=current_interp_factor,
                              enable_peaks=enable_peaks, peak_prominence=current_peak_prominence, peak_width=current_peak_width,
                              enable_linreg=enable_linreg, show_linreg_eq=show_linreg_eq, show_linreg_r2=show_linreg_r2, show_linreg_p_value=show_linreg_p_value, show_linreg_str_err=show_linreg_str_err,
                              extra_axes=extra_axes)

            # 坐标轴设置
            if log_x: ax.set_xscale('log')
            if log_y: ax.set_yscale('log')
            if invert_x: ax.invert_xaxis()
            if invert_y: ax.invert_yaxis()
            
            # 坐标轴范围手动设置
            if x_min:
                try: ax.set_xlim(left=float(x_min))
                except: pass
            if x_max:
                try: ax.set_xlim(right=float(x_max))
                except: pass
            if y_min:
                try: ax.set_ylim(bottom=float(y_min))
                except: pass
            if y_max:
                try: ax.set_ylim(top=float(y_max))
                except: pass

            # 通用设置
            ax.set_title(plot_title, fontsize=font_size+2, pad=15)
            if plot_type not in ["Pie Chart (饼图)", "Correlation Heatmap (相关性热力图)"]:
                if x_label: ax.set_xlabel(x_label, fontsize=font_size)
                if y_label: ax.set_ylabel(y_label, fontsize=font_size)
            
            if show_grid and plot_type not in ["Pie Chart (饼图)", "Correlation Heatmap (相关性热力图)"]:
                ax.grid(True, linestyle='--', alpha=0.7)
            
            if plot_type not in ["Histogram (直方图)", "Pie Chart (饼图)", "Correlation Heatmap (相关性热力图)"] and len(y_cols) > 0 and show_legend:
                if hasattr(ax, 'custom_handles') and ax.custom_handles:
                    ax.legend(handles=ax.custom_handles, labels=ax.custom_labels, loc=legend_loc)
                else:
                    ax.legend(loc=legend_loc)

            st.pyplot(fig)
            
            # 提供高分辨率下载
            import io
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
            img_buffer.seek(0)
                           
            st.download_button(
                label="下载 (PNG)",
                data=img_buffer,
                file_name="plot.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"绘图错误: {e}")
            st.info("请检查您的数据列是否包含非数值类型, 或者X/Y轴选择是否正确。")
    else:
        st.warning("暂无数据")

with tab3:
    st.markdown("### 展示代码")
    st.caption("以下代码可直接复制并在本地 Python 环境中运行, 以供学习参考。")
    
    df_plot = st.session_state.df
    
    if len(df_plot) > 0:
        try:
            # 准备参数，处理可能未定义的变量
            current_bins = bins if 'bins' in locals() else 20
            current_interp_kind = interp_kind if 'interp_kind' in locals() else 'linear'
            current_interp_factor = interp_factor if 'interp_factor' in locals() else 5
            current_peak_prominence = peak_prominence if 'peak_prominence' in locals() else 0.1
            current_peak_width = peak_width if 'peak_width' in locals() else 0.0
            
            code = generate_plot_code(plot_type, df_plot, x_col, y_cols, 
                                    marker_style_val, line_style_val, line_width, marker_size, alpha, font_size,
                                    bins=current_bins, 
                                    enable_interp=enable_interp, interp_kind=current_interp_kind, interp_factor=current_interp_factor,
                                    enable_peaks=enable_peaks, peak_prominence=current_peak_prominence, peak_width=current_peak_width,
                                    enable_linreg=enable_linreg, show_linreg_eq=show_linreg_eq, show_linreg_r2=show_linreg_r2, show_linreg_p_value=show_linreg_p_value, show_linreg_str_err=show_linreg_str_err,
                                    plot_title=plot_title, x_label=x_label, y_label=y_label,
                                    show_grid=show_grid, show_legend=show_legend, legend_loc=legend_loc,
                                    log_x=log_x, log_y=log_y, invert_x=invert_x, invert_y=invert_y,
                                    x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,
                                    theme_style=theme_style, font_family=font_family,
                                    extra_axes=extra_axes
                                )
            
            st.code(code, language='python')
        except Exception as e:
            st.error(f"代码生成错误: {e}")
    else:
        st.warning("暂无数据")

