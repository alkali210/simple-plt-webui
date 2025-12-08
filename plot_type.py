import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate, signal, stats

def draw_plot_content(ax, plot_type, df_plot, x_col, y_cols, 
                      marker_style_val, line_style_val, line_width, marker_size, alpha, font_size,
                      bins=20, 
                      enable_interp=False, interp_kind='linear', interp_factor=5,
                      enable_peaks=False, peak_prominence=0.1, peak_width=0.0,
                      enable_linreg=False):
    match plot_type:
        case "Line Plot (折线图)":
            for y_col in y_cols:
                x_data = df_plot[x_col]
                y_data = df_plot[y_col]
                
                # 插值处理
                if enable_interp and len(x_data) > 3:
                    try:
                        # 确保数据排序
                        sorted_indices = np.argsort(x_data)
                        x_sorted = x_data.iloc[sorted_indices]
                        y_sorted = y_data.iloc[sorted_indices]
                        
                        if interp_kind == 'spline':
                            # 使用 B-Spline
                            t, c, k = interpolate.splrep(x_sorted, y_sorted, s=0, k=3)
                            x_new = np.linspace(x_sorted.min(), x_sorted.max(), len(x_sorted) * interp_factor)
                            bspline = interpolate.BSpline(t, c, k, extrapolate=False)
                            y_new = bspline(x_new)
                        else:
                            f = interpolate.interp1d(x_sorted, y_sorted, kind=interp_kind)
                            x_new = np.linspace(x_sorted.min(), x_sorted.max(), len(x_sorted) * interp_factor)
                            y_new = f(x_new)
                        
                        ax.plot(x_new, y_new, 
                                marker='', linestyle=line_style_val, 
                                linewidth=line_width, label=f"{y_col} (smooth)", alpha=alpha)
                        # 原始点
                        ax.scatter(x_data, y_data, marker=marker_style_val, s=marker_size/5, alpha=0.5)
                    except Exception as e:
                        st.warning(f"插值失败 ({y_col}): {e}")
                        ax.plot(x_data, y_data, 
                                marker=marker_style_val, linestyle=line_style_val, 
                                linewidth=line_width, markersize=marker_size/5,
                                label=y_col, alpha=alpha)
                else:
                    ax.plot(x_data, y_data, 
                            marker=marker_style_val, linestyle=line_style_val, 
                            linewidth=line_width, markersize=marker_size/5,
                            label=y_col, alpha=alpha)
                
                # 寻峰处理
                if enable_peaks:
                    try:
                        peaks, _ = signal.find_peaks(y_data, prominence=peak_prominence, width=peak_width)
                        if len(peaks) > 0:
                            ax.plot(x_data.iloc[peaks], y_data.iloc[peaks], "x", color='red', markersize=10, label=f"{y_col} peaks")
                    except Exception as e:
                        st.warning(f"寻峰失败 ({y_col}): {e}")

                # 线性回归
                if enable_linreg:
                    try:
                        # 移除 NaN
                        mask = ~np.isnan(x_data) & ~np.isnan(y_data)
                        x_clean = x_data[mask]
                        y_clean = y_data[mask]
                        
                        if len(x_clean) > 1:
                            slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
                            
                            # 绘制回归线
                            line_x = np.array([x_clean.min(), x_clean.max()])
                            line_y = slope * line_x + intercept
                            
                            if intercept >= 0: label_text = rf"$linReg: y={slope:.4f}x+{intercept:.4f}, r={r_value:.4f}$"
                            else: label_text = rf"$linReg: y={slope:.4f}x{intercept:.4f}, r={r_value:.4f}$"

                            ax.plot(line_x, line_y, linestyle='--', linewidth=line_width, label=label_text)
                    except Exception as e:
                        st.warning(f"回归分析失败 ({y_col}): {e}")

        case "Scatter Plot (散点图)":
            for y_col in y_cols:
                ax.scatter(df_plot[x_col], df_plot[y_col], 
                           marker=marker_style_val, s=marker_size, 
                           label=y_col, alpha=alpha)
                
                # 线性回归
                if enable_linreg:
                    try:
                        x_data = df_plot[x_col]
                        y_data = df_plot[y_col]
                        # 移除 NaN
                        mask = ~np.isnan(x_data) & ~np.isnan(y_data)
                        x_clean = x_data[mask]
                        y_clean = y_data[mask]
                        
                        if len(x_clean) > 1:
                            slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
                            
                            # 绘制回归线
                            line_x = np.array([x_clean.min(), x_clean.max()])
                            line_y = slope * line_x + intercept
                            
                            if intercept >= 0: label_text = rf"$linReg: y={slope:.4f}x+{intercept:.4f}, r={r_value:.4f}$"
                            else: label_text = rf"$linReg: y={slope:.4f}x{intercept:.4f}, r={r_value:.4f}$"
                            ax.plot(line_x, line_y, linestyle='--', linewidth=line_width, label=label_text)
                    except Exception as e:
                        st.warning(f"回归分析失败 ({y_col}): {e}")

        case "Bar Chart (柱状图)":
            # 简单的多列柱状图处理
            x = np.arange(len(df_plot))
            width = 0.8 / len(y_cols) if len(y_cols) > 0 else 0.8
        
            for i, y_col in enumerate(y_cols):
                offset = (i - len(y_cols)/2) * width + width/2
                ax.bar(x + offset, df_plot[y_col], width, label=y_col, alpha=alpha)
        
            ax.set_xticks(x)
            ax.set_xticklabels(df_plot[x_col], rotation=45)
        
        case "Histogram (直方图)":
            ax.hist(df_plot[x_col], bins=bins, alpha=alpha, color='#0078d4', edgecolor='black')

        case "Box Plot (箱线图)":
            data_to_plot = [df_plot[col].dropna() for col in y_cols]
            ax.boxplot(data_to_plot, labels=y_cols, patch_artist=True, 
                       boxprops=dict(facecolor='#0078d4', alpha=alpha))

        case "Pie Chart (饼图)":
            # 饼图通常聚合数据
            if len(y_cols) > 0:
                y_col = y_cols[0]
                ax.pie(df_plot[y_col], labels=df_plot[x_col], autopct='%1.1f%%', startangle=90,
                       textprops={'fontsize': font_size})

        case "Area Chart (面积图)":
            for y_col in y_cols:
                ax.fill_between(df_plot[x_col], df_plot[y_col], alpha=alpha, label=y_col)
                ax.plot(df_plot[x_col], df_plot[y_col], label=f"_{y_col}", linewidth=1) # 辅助线

        case "Violin Plot (小提琴图)":
            data_to_plot = [df_plot[col].dropna() for col in y_cols]
            parts = ax.violinplot(data_to_plot, showmeans=False, showmedians=True)
            for pc in parts['bodies']:
                pc.set_facecolor('#0078d4')
                pc.set_alpha(alpha)
            ax.set_xticks(np.arange(1, len(y_cols) + 1))
            ax.set_xticklabels(y_cols)

        case "Correlation Heatmap (相关性热力图)":
            # 计算相关性矩阵
            corr = df_plot.select_dtypes(include=[np.number]).corr()
            im = ax.imshow(corr, cmap='coolwarm', interpolation='nearest')
            plt.colorbar(im, ax=ax)
            # 添加标签
            tick_marks = np.arange(len(corr.columns))
            ax.set_xticks(tick_marks)
            ax.set_yticks(tick_marks)
            ax.set_xticklabels(corr.columns, rotation=45)
            ax.set_yticklabels(corr.columns)
            # 在格子上显示数值
            for i in range(len(corr.columns)):
                for j in range(len(corr.columns)):
                    text = ax.text(j, i, f"{corr.iloc[i, j]:.2f}",
                                   ha="center", va="center", color="black", fontsize=font_size-2)
        
