def generate_plot_code(plot_type, df_plot, x_col, y_cols, 
                      marker_style_val, line_style_val, line_width, marker_size, alpha, font_size,
                      bins=20, 
                      enable_interp=False, interp_kind='linear', interp_factor=5,
                      enable_peaks=False, peak_prominence=0.1, peak_width=0.0,
                      enable_linreg=False,
                      plot_title="", x_label="", y_label="",
                      show_grid=True, show_legend=True, legend_loc="best",
                      log_x=False, log_y=False, invert_x=False, invert_y=False,
                      x_min="", x_max="", y_min="", y_max="",
                      theme_style="default", font_family="SimHei"):
    
    code = []
    
    # Imports
    code.append("import matplotlib.pyplot as plt")
    code.append("import pandas as pd")
    code.append("import numpy as np")
    if enable_interp or enable_linreg or enable_peaks:
        code.append("from scipy import interpolate, signal, stats")
    code.append("")

    # Style setup
    code.append(f"# 设置样式")
    code.append(f"plt.style.use('{theme_style}')")
    code.append(f"plt.rcParams.update({{")
    code.append(f"    'font.sans-serif': ['{font_family}', 'Microsoft YaHei', 'SimHei', 'Arial', 'sans-serif'],")
    code.append(f"    'axes.unicode_minus': False,")
    code.append(f"    'font.size': {font_size}")
    code.append(f"}})")
    code.append("")

    # Data
    # Convert dataframe to dictionary for cleaner representation in code
    # We only include columns that are actually used to keep it cleaner if possible, 
    # but to be safe and simple, we can just dump the whole df if it's small, 
    # or just the relevant columns. Let's try to be smart.
    used_cols = set()
    if x_col: used_cols.add(x_col)
    for c in y_cols: used_cols.add(c)
    
    # If df is too large, this might be an issue, but for this task we assume it fits or user accepts it.
    # We filter the df to only used columns to save space.
    if used_cols:
        df_subset = df_plot[list(used_cols)]
        data_dict = df_subset.to_dict(orient='list')
    else:
        data_dict = df_plot.to_dict(orient='list')

    code.append("# 准备数据")
    code.append(f"data = {data_dict}")
    code.append("df = pd.DataFrame(data)")
    code.append("")
    
    # Plot setup
    code.append("# 创建图表")
    code.append("fig, ax = plt.subplots(figsize=(10, 6))")
    code.append("")

    # Plot logic based on type
    if plot_type == "Line Plot (折线图)":
        code.append(f"# 绘制折线图")
        code.append(f"y_cols = {y_cols}")
        code.append(f"for y_col in y_cols:")
        code.append(f"    x_data = df['{x_col}']")
        code.append(f"    y_data = df[y_col]")
        
        if enable_interp:
            code.append(f"    # 插值处理")
            code.append(f"    if len(x_data) > 3:")
            code.append(f"        sorted_indices = np.argsort(x_data)")
            code.append(f"        x_sorted = x_data.iloc[sorted_indices]")
            code.append(f"        y_sorted = y_data.iloc[sorted_indices]")
            
            if interp_kind == 'spline':
                code.append(f"        # 使用 B-Spline")
                code.append(f"        t, c, k = interpolate.splrep(x_sorted, y_sorted, s=0, k=3)")
                code.append(f"        x_new = np.linspace(x_sorted.min(), x_sorted.max(), len(x_sorted) * {interp_factor})")
                code.append(f"        bspline = interpolate.BSpline(t, c, k, extrapolate=False)")
                code.append(f"        y_new = bspline(x_new)")
            else:
                code.append(f"        f = interpolate.interp1d(x_sorted, y_sorted, kind='{interp_kind}')")
                code.append(f"        x_new = np.linspace(x_sorted.min(), x_sorted.max(), len(x_sorted) * {interp_factor})")
                code.append(f"        y_new = f(x_new)")
            
            code.append(f"        ax.plot(x_new, y_new, marker='', linestyle='{line_style_val}', linewidth={line_width}, label=f'{{y_col}} (smooth)', alpha={alpha})")
            code.append(f"        ax.scatter(x_data, y_data, marker='{marker_style_val}', s={marker_size}/5, alpha=0.5)")
            code.append(f"    else:")
            code.append(f"        ax.plot(x_data, y_data, marker='{marker_style_val}', linestyle='{line_style_val}', linewidth={line_width}, markersize={marker_size}/5, label=y_col, alpha={alpha})")
        else:
            code.append(f"    ax.plot(x_data, y_data, marker='{marker_style_val}', linestyle='{line_style_val}', linewidth={line_width}, markersize={marker_size}/5, label=y_col, alpha={alpha})")

        if enable_peaks:
            code.append(f"    # 寻峰处理")
            code.append(f"    peaks, _ = signal.find_peaks(y_data, prominence={peak_prominence}, width={peak_width})")
            code.append(f"    if len(peaks) > 0:")
            code.append(f"        ax.plot(x_data.iloc[peaks], y_data.iloc[peaks], 'x', color='red', markersize=10, label=f'{{y_col}} peaks')")

        if enable_linreg:
            code.append(f"    # 线性回归")
            code.append(f"    mask = ~np.isnan(x_data) & ~np.isnan(y_data)")
            code.append(f"    x_clean = x_data[mask]")
            code.append(f"    y_clean = y_data[mask]")
            code.append(f"    if len(x_clean) > 1:")
            code.append(f"        slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)")
            code.append(f"        line_x = np.array([x_clean.min(), x_clean.max()])")
            code.append(f"        line_y = slope * line_x + intercept")
            code.append(f"        label_text = rf'$linReg: y={{slope:.4f}}x+{{intercept:.4f}}, r={{r_value:.4f}}$' if intercept >= 0 else rf'$linReg: y={{slope:.4f}}x{{intercept:.4f}}, r={{r_value:.4f}}$'")
            code.append(f"        ax.plot(line_x, line_y, linestyle='--', linewidth={line_width}, label=label_text)")

    elif plot_type == "Scatter Plot (散点图)":
        code.append(f"# 绘制散点图")
        code.append(f"y_cols = {y_cols}")
        code.append(f"for y_col in y_cols:")
        code.append(f"    ax.scatter(df['{x_col}'], df[y_col], marker='{marker_style_val}', s={marker_size}, label=y_col, alpha={alpha})")
        
        if enable_linreg:
            code.append(f"    # 线性回归")
            code.append(f"    x_data = df['{x_col}']")
            code.append(f"    y_data = df[y_col]")
            code.append(f"    mask = ~np.isnan(x_data) & ~np.isnan(y_data)")
            code.append(f"    x_clean = x_data[mask]")
            code.append(f"    y_clean = y_data[mask]")
            code.append(f"    if len(x_clean) > 1:")
            code.append(f"        slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)")
            code.append(f"        line_x = np.array([x_clean.min(), x_clean.max()])")
            code.append(f"        line_y = slope * line_x + intercept")
            code.append(f"        label_text = rf'$linReg: y={{slope:.4f}}x+{{intercept:.4f}}, r={{r_value:.4f}}$' if intercept >= 0 else rf'$linReg: y={{slope:.4f}}x{{intercept:.4f}}, r={{r_value:.4f}}$'")
            code.append(f"        ax.plot(line_x, line_y, linestyle='--', linewidth={line_width}, label=label_text)")

    elif plot_type == "Bar Chart (柱状图)":
        code.append(f"# 绘制柱状图")
        code.append(f"y_cols = {y_cols}")
        code.append(f"x = np.arange(len(df))")
        code.append(f"width = 0.8 / len(y_cols) if len(y_cols) > 0 else 0.8")
        code.append(f"for i, y_col in enumerate(y_cols):")
        code.append(f"    offset = (i - len(y_cols)/2) * width + width/2")
        code.append(f"    ax.bar(x + offset, df[y_col], width, label=y_col, alpha={alpha})")
        code.append(f"ax.set_xticks(x)")
        code.append(f"ax.set_xticklabels(df['{x_col}'], rotation=45)")

    elif plot_type == "Histogram (直方图)":
        code.append(f"# 绘制直方图")
        code.append(f"ax.hist(df['{x_col}'], bins={bins}, alpha={alpha}, color='#0078d4', edgecolor='black')")

    elif plot_type == "Box Plot (箱线图)":
        code.append(f"# 绘制箱线图")
        code.append(f"y_cols = {y_cols}")
        code.append(f"data_to_plot = [df[col].dropna() for col in y_cols]")
        code.append(f"ax.boxplot(data_to_plot, labels=y_cols, patch_artist=True, boxprops=dict(facecolor='#0078d4', alpha={alpha}))")

    elif plot_type == "Pie Chart (饼图)":
        code.append(f"# 绘制饼图")
        code.append(f"y_cols = {y_cols}")
        code.append(f"if len(y_cols) > 0:")
        code.append(f"    y_col = y_cols[0]")
        code.append(f"    ax.pie(df[y_col], labels=df['{x_col}'], autopct='%1.1f%%', startangle=90, textprops={{'fontsize': {font_size}}})")

    elif plot_type == "Area Chart (面积图)":
        code.append(f"# 绘制面积图")
        code.append(f"y_cols = {y_cols}")
        code.append(f"for y_col in y_cols:")
        code.append(f"    ax.fill_between(df['{x_col}'], df[y_col], alpha={alpha}, label=y_col)")
        code.append(f"    ax.plot(df['{x_col}'], df[y_col], label=f'_{{y_col}}', linewidth=1)")

    elif plot_type == "Violin Plot (小提琴图)":
        code.append(f"# 绘制小提琴图")
        code.append(f"y_cols = {y_cols}")
        code.append(f"data_to_plot = [df[col].dropna() for col in y_cols]")
        code.append(f"parts = ax.violinplot(data_to_plot, showmeans=False, showmedians=True)")
        code.append(f"for pc in parts['bodies']:")
        code.append(f"    pc.set_facecolor('#0078d4')")
        code.append(f"    pc.set_alpha({alpha})")
        code.append(f"ax.set_xticks(np.arange(1, len(y_cols) + 1))")
        code.append(f"ax.set_xticklabels(y_cols)")

    elif plot_type == "Correlation Heatmap (相关性热力图)":
        code.append(f"# 绘制相关性热力图")
        code.append(f"corr = df.select_dtypes(include=[np.number]).corr()")
        code.append(f"im = ax.imshow(corr, cmap='coolwarm', interpolation='nearest')")
        code.append(f"plt.colorbar(im, ax=ax)")
        code.append(f"tick_marks = np.arange(len(corr.columns))")
        code.append(f"ax.set_xticks(tick_marks)")
        code.append(f"ax.set_yticks(tick_marks)")
        code.append(f"ax.set_xticklabels(corr.columns, rotation=45)")
        code.append(f"ax.set_yticklabels(corr.columns)")
        code.append(f"for i in range(len(corr.columns)):")
        code.append(f"    for j in range(len(corr.columns)):")
        code.append(f"        text = ax.text(j, i, f'{{corr.iloc[i, j]:.2f}}', ha='center', va='center', color='black', fontsize={font_size}-2)")

    # Common styling
    code.append("")
    code.append("# 通用设置")
    
    # Axis settings
    if log_x: code.append("ax.set_xscale('log')")
    if log_y: code.append("ax.set_yscale('log')")
    if invert_x: code.append("ax.invert_xaxis()")
    if invert_y: code.append("ax.invert_yaxis()")
    
    if x_min: code.append(f"try: ax.set_xlim(left={x_min})\nexcept: pass")
    if x_max: code.append(f"try: ax.set_xlim(right={x_max})\nexcept: pass")
    if y_min: code.append(f"try: ax.set_ylim(bottom={y_min})\nexcept: pass")
    if y_max: code.append(f"try: ax.set_ylim(top={y_max})\nexcept: pass")

    code.append(f"ax.set_title('{plot_title}', fontsize={font_size}+2, pad=15)")
    
    if plot_type not in ["Pie Chart (饼图)", "Correlation Heatmap (相关性热力图)"]:
        if x_label: code.append(f"ax.set_xlabel('{x_label}', fontsize={font_size})")
        if y_label: code.append(f"ax.set_ylabel('{y_label}', fontsize={font_size})")
    
    if show_grid and plot_type not in ["Pie Chart (饼图)", "Correlation Heatmap (相关性热力图)"]:
        code.append("ax.grid(True, linestyle='--', alpha=0.7)")
    
    if plot_type not in ["Histogram (直方图)", "Pie Chart (饼图)", "Correlation Heatmap (相关性热力图)"] and len(y_cols) > 0 and show_legend:
        code.append(f"ax.legend(loc='{legend_loc}')")

    code.append("plt.tight_layout()")
    code.append("plt.show()")

    return "\n".join(code)
