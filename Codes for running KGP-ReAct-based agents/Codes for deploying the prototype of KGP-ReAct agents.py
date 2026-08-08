import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageChops
import subprocess
import ctypes

# Improve Windows DPI rendering clarity. This only affects visual scaling.
def enable_windows_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ====== 1. 主题常量（仅视觉优化，不改业务逻辑） ======
BG_COLOR           = "#F3F7FC"   # 整体背景
SURFACE_COLOR      = "#FFFFFF"   # 卡片背景
SURFACE_ALT        = "#F7FAFE"   # 次级区域背景
HEADER_BG          = "#EDF5FF"   # 顶部标题栏背景
BORDER_COLOR       = "#BED2E8"   # 边框颜色
TEXT_PRIMARY       = "#102B46"   # 主文字：加深，提高对比度
TEXT_SECONDARY     = "#2F5274"   # 次文字：加深，提高可读性
ACCENT_GREEN       = "#20C4CF"   # KGP 主色（仅视觉）
ACCENT_PURPLE      = "#F4B23D"   # ReAct 主色（仅视觉）
ACCENT_BLUE        = "#4F8CFF"   # Update 主强调色
BTN_DEFAULT_BG     = "#E7F0FA"   # 次按钮底色
BTN_DEFAULT_FG     = "#18324A"   # 次按钮文字
INPUT_BG           = "#FFFFFF"   # 输入框背景
OUTPUT_BG          = "#FBFDFF"   # 控制台背景
OUTPUT_FG          = "#102B46"   # 控制台文字

# 字体统一：普通说明文字 22，其余主要界面文字 30。
# 只改变视觉字号，不改变任何业务逻辑。
FONT_HERO          = ("Segoe UI", 30, "bold")
FONT_HEADER_TITLE  = ("Segoe UI", 30, "bold")
FONT_TITLE         = ("Segoe UI", 30, "bold")
FONT_LABEL         = ("Segoe UI", 22)
FONT_BUTTON        = ("Segoe UI", 30, "bold")
FONT_ACCENT_BUTTON = ("Segoe UI", 30, "bold")
FONT_ENTRY         = ("Segoe UI", 30)
FONT_CONSOLE       = ("Consolas", 30)

# Static balancing space for the right panel. This avoids resize jitter while keeping
# the two output areas visually aligned with less empty space above the ReAct output.
REACT_OUTPUT_TOP_SPACER = 28

# ====== 2. 公共函数区 ======
def select_file(entry):
    path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def run_script(command, text_output):
    text_output.insert(tk.END, "\n[INFO] Script running...\n")
    text_output.see(tk.END)
    root.update()
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1
    )
    for line in iter(proc.stdout.readline, ""):
        text_output.insert(tk.END, line)
        text_output.see(tk.END)
        root.update()
    proc.stdout.close()
    proc.wait()
    text_output.insert(tk.END, "\n[INFO] Execution completed!\n")
    text_output.see(tk.END)
    root.update()

def clear_console(text_output):
    text_output.delete("1.0", tk.END)

def create_responsive_logo(parent, image_path, bg_color, max_height=74, horizontal_padding=80):
    original_img = Image.open(image_path)
    logo_label = tk.Label(parent, bg=bg_color, bd=0)
    logo_label.grid(row=0, column=0, pady=12)

    def update_logo(event=None):
        available_width = max(parent.winfo_width() - horizontal_padding, 120)
        aspect_ratio = original_img.height / original_img.width

        new_width = available_width
        new_height = int(new_width * aspect_ratio)

        if new_height > max_height:
            new_height = max_height
            new_width = int(new_height / aspect_ratio)

        resized = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        logo_label.configure(image=photo)
        logo_label.image = photo

    parent.bind("<Configure>", update_logo)
    parent.after(100, update_logo)
    return logo_label

def extract_logo_icon(original_img):
    """Extract only the colored logo mark from a wide logo image.

    The old logo file may contain both the icon and the original title text.
    This keeps the icon itself unchanged while preventing the first letters
    of the old title from being displayed next to it.
    """
    rgba_img = original_img.convert("RGBA")
    hsv_img = rgba_img.convert("HSV")

    saturation = hsv_img.getchannel("S")
    value = hsv_img.getchannel("V")
    alpha = rgba_img.getchannel("A")

    # The icon is cyan/purple and highly saturated; the old title text is dark
    # and low-saturation. This mask isolates the icon instead of cropping into
    # the first letters of the title.
    saturation_mask = saturation.point(lambda x: 255 if x > 45 else 0)
    value_mask = value.point(lambda x: 255 if x > 110 else 0)
    alpha_mask = alpha.point(lambda x: 255 if x > 10 else 0)
    icon_mask = ImageChops.multiply(saturation_mask, value_mask)
    icon_mask = ImageChops.multiply(icon_mask, alpha_mask)

    bbox = icon_mask.getbbox()
    if bbox:
        pad = 6
        left = max(bbox[0] - pad, 0)
        top = max(bbox[1] - pad, 0)
        right = min(bbox[2] + pad, rgba_img.width)
        bottom = min(bbox[3] + pad, rgba_img.height)
        return rgba_img.crop((left, top, right, bottom))

    # Fallback: keep only the left square-ish logo area if color detection fails.
    fallback_width = min(rgba_img.width, int(rgba_img.height * 0.95))
    return rgba_img.crop((0, 0, fallback_width, rgba_img.height))

def create_header_icon_and_title(parent, image_path, bg_color):
    """Top banner: keep the logo icon, but draw the title as editable text."""
    title_text = "Smart Agent for Managing Interdependent Infrastructure Networks in Pre-Rainfall Scenarios"

    header_inner = tk.Frame(parent, bg=bg_color)
    header_inner.grid(row=0, column=0, pady=14)

    try:
        original_img = Image.open(image_path)
        icon_img = extract_logo_icon(original_img)
        icon_img.thumbnail((50, 50), Image.Resampling.LANCZOS)
        icon_photo = ImageTk.PhotoImage(icon_img)

        icon_label = tk.Label(header_inner, image=icon_photo, bg=bg_color, bd=0)
        icon_label.image = icon_photo
        icon_label.grid(row=0, column=0, sticky="w", padx=(0, 14))
    except Exception as e:
        print("Logo 图标加载失败：", e)

    tk.Label(
        header_inner,
        text=title_text,
        font=FONT_HEADER_TITLE,
        fg=TEXT_PRIMARY,
        bg=bg_color,
        anchor="w",
        justify="left"
    ).grid(row=0, column=1, sticky="w")

def toggle_api_visibility():
    if entry_api_plan.cget("show") == "*":
        entry_api_plan.config(show="")
        toggle_button.config(text="Hide Key")
    else:
        entry_api_plan.config(show="*")
        toggle_button.config(text="Show Key")

def create_card(parent, row, column, padx=(0, 0), pady=(0, 0)):
    card = tk.Frame(
        parent,
        bg=SURFACE_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
        bd=0
    )
    card.grid(row=row, column=column, sticky="nsew", padx=padx, pady=pady)
    return card

def add_card_header(parent, title, accent):
    header = tk.Frame(parent, bg=SURFACE_COLOR)
    header.pack(fill="x", padx=20, pady=(14, 8))

    accent_bar = tk.Frame(header, bg=accent, width=6, height=40)
    accent_bar.pack(side="left", fill="y", padx=(0, 12))

    tk.Label(
        header,
        text=title,
        font=FONT_TITLE,
        fg=TEXT_PRIMARY,
        bg=SURFACE_COLOR,
        anchor="w"
    ).pack(side="left", anchor="w")

def add_section_title(parent, text):
    section = tk.Frame(parent, bg=SURFACE_COLOR)
    section.pack(fill="x", padx=20, pady=(2, 4))

    tk.Label(
        section,
        text=text,
        font=FONT_TITLE,
        fg=TEXT_PRIMARY,
        bg=SURFACE_COLOR,
        anchor="w"
    ).pack(side="left")

    divider = tk.Frame(section, bg=BORDER_COLOR, height=1)
    divider.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=8)

def style_text_widget(text_widget, height):
    text_widget.configure(
        height=height,
        bg=OUTPUT_BG,
        fg=OUTPUT_FG,
        insertbackground=TEXT_PRIMARY,
        selectbackground="#CFE3FF",
        selectforeground=TEXT_PRIMARY,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        relief="flat",
        font=FONT_CONSOLE,
        wrap="word",
        padx=10,
        pady=10,
        spacing1=3,
        spacing3=3
    )

def open_update_tool():
    update_window = tk.Toplevel(root)
    update_window.title("Tool Updating Interface")
    update_window.geometry("980x800")
    update_window.minsize(900, 760)
    update_window.configure(bg=BG_COLOR)
    update_window.columnconfigure(0, weight=1)
    update_window.rowconfigure(1, weight=1)

    local_style = ttk.Style(update_window)
    local_style.theme_use("clam")
    local_style.configure(
        "AccentBlue.TButton",
        font=FONT_ACCENT_BUTTON,
        foreground="white",
        background=ACCENT_BLUE,
        borderwidth=0,
        padding=(14, 8)
    )
    local_style.map(
        "AccentBlue.TButton",
        background=[("active", "#3A73DD")]
    )
    local_style.configure(
        "Default.TButton",
        font=FONT_BUTTON,
        foreground=BTN_DEFAULT_FG,
        background=BTN_DEFAULT_BG,
        borderwidth=0,
        padding=(12, 7)
    )
    local_style.map(
        "Default.TButton",
        background=[("active", "#223150")]
    )
    local_style.configure(
        "Modern.TEntry",
        fieldbackground=INPUT_BG,
        foreground=TEXT_PRIMARY,
        bordercolor=BORDER_COLOR,
        lightcolor=BORDER_COLOR,
        darkcolor=BORDER_COLOR,
        insertcolor=TEXT_PRIMARY,
        padding=(8, 6)
    )

    header = tk.Frame(
        update_window,
        bg=HEADER_BG,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
        bd=0,
        height=90
    )
    header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
    header.grid_propagate(False)
    header.columnconfigure(0, weight=1)

    tk.Label(
        header,
        text="Update IIN-PRS Tool kit",
        font=FONT_HERO,
        fg=TEXT_PRIMARY,
        bg=HEADER_BG,
        anchor="w"
    ).grid(row=0, column=0, sticky="w", padx=24, pady=24)

    body = tk.Frame(update_window, bg=BG_COLOR)
    body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
    body.columnconfigure(0, weight=1)
    body.rowconfigure(0, weight=1)

    content_card = tk.Frame(
        body,
        bg=SURFACE_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
        bd=0
    )
    content_card.grid(row=0, column=0, sticky="nsew")
    content_card.columnconfigure(0, weight=1)

    inner = tk.Frame(content_card, bg=SURFACE_COLOR)
    inner.pack(fill="both", expand=True, padx=20, pady=20)
    inner.columnconfigure(0, weight=1)
    inner.columnconfigure(1, weight=1)

    # =====================================================================
    # 1. Tool Uploading
    # =====================================================================
    tool_path_frame = tk.Frame(
        inner,
        bg=SURFACE_ALT,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
        bd=0
    )
    tool_path_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
    tool_path_frame.columnconfigure(0, weight=1)

    tk.Label(
        tool_path_frame,
        text="Tool Uploading",
        font=FONT_TITLE,
        fg=ACCENT_BLUE,
        bg=SURFACE_ALT
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 8))

    tk.Label(
        tool_path_frame,
        text="Please fill in the path of tool's function (.py):",
        font=FONT_LABEL,
        fg=TEXT_PRIMARY,
        bg=SURFACE_ALT
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 4))

    entry_tool_path = ttk.Entry(tool_path_frame, font=FONT_ENTRY, style="Modern.TEntry")
    entry_tool_path.grid(row=2, column=0, sticky="ew", padx=(16, 8), pady=(0, 12))

    def browse_py_file():
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if path:
            entry_tool_path.delete(0, tk.END)
            entry_tool_path.insert(0, path)

    ttk.Button(
        tool_path_frame,
        text="Browse",
        command=browse_py_file,
        style="Default.TButton"
    ).grid(row=2, column=1, sticky="e", padx=(0, 16), pady=(0, 12))

    tk.Label(
        tool_path_frame,
        text="Please fill in the name of tool's function:",
        font=FONT_LABEL,
        fg=TEXT_PRIMARY,
        bg=SURFACE_ALT
    ).grid(row=3, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 4))

    entry_tool_function = ttk.Entry(tool_path_frame, font=FONT_ENTRY, style="Modern.TEntry")
    entry_tool_function.grid(row=4, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))

    # =====================================================================
    # 2. Tool Description Filling
    # =====================================================================
    tool_desc_frame = tk.Frame(
        inner,
        bg=SURFACE_ALT,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
        bd=0
    )
    tool_desc_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 14))
    tool_desc_frame.columnconfigure(0, weight=1)
    tool_desc_frame.columnconfigure(1, weight=1)

    tk.Label(
        tool_desc_frame,
        text="Tool Description Filling",
        font=FONT_TITLE,
        fg=ACCENT_BLUE,
        bg=SURFACE_ALT
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 10))

    def create_labeled_entry(parent, label_text, row, column):
        tk.Label(
            parent,
            text=label_text,
            font=FONT_LABEL,
            fg=TEXT_PRIMARY,
            bg=SURFACE_ALT,
            anchor="w",
            justify="left",
            wraplength=420
        ).grid(row=row, column=column, sticky="w", padx=16, pady=(0, 4))
        e = ttk.Entry(parent, font=FONT_ENTRY, style="Modern.TEntry")
        e.grid(row=row + 1, column=column, sticky="ew", padx=16, pady=(0, 12))
        return e

    entry_purpose = create_labeled_entry(tool_desc_frame, "Purpose of the tool:", 1, 0)
    entry_input   = create_labeled_entry(tool_desc_frame, "Input of the tool:", 1, 1)
    entry_output  = create_labeled_entry(tool_desc_frame, "Output of the tool:", 3, 0)
    entry_outcome = create_labeled_entry(tool_desc_frame, "Effect of using the tool:", 3, 1)

    # =====================================================================
    # 3. Tool Graph Updating
    # =====================================================================
    tool_graph_frame = tk.Frame(
        inner,
        bg=SURFACE_ALT,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
        bd=0
    )
    tool_graph_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    tool_graph_frame.columnconfigure(0, weight=1)

    tk.Label(
        tool_graph_frame,
        text="Tool Graph Updating",
        font=FONT_TITLE,
        fg=ACCENT_BLUE,
        bg=SURFACE_ALT
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 8))

    tk.Label(
        tool_graph_frame,
        text="Please upload the updated tool graph (.json):",
        font=FONT_LABEL,
        fg=TEXT_PRIMARY,
        bg=SURFACE_ALT
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 4))

    entry_tool_graph = ttk.Entry(tool_graph_frame, font=FONT_ENTRY, style="Modern.TEntry")
    entry_tool_graph.grid(row=2, column=0, sticky="ew", padx=(16, 8), pady=(0, 16))

    def browse_json_file():
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            entry_tool_graph.delete(0, tk.END)
            entry_tool_graph.insert(0, path)

    ttk.Button(
        tool_graph_frame,
        text="Browse",
        command=browse_json_file,
        style="Default.TButton"
    ).grid(row=2, column=1, sticky="e", padx=(0, 16), pady=(0, 16))

    # =====================================================================
    # 4. 逻辑：更新工具（沿用你原来的文件操作）
    # =====================================================================
    def update_tool():
        tool_path     = entry_tool_path.get()   # 目前没用到，但先保留
        tool_function = entry_tool_function.get()
        purpose       = entry_purpose.get()
        tool_input    = entry_input.get()
        tool_output   = entry_output.get()
        outcome       = entry_outcome.get()
        tool_graph    = entry_tool_graph.get()

        import_statement = f"from {tool_function} import {tool_function}\n"
        tool_definition  = (
            f"{tool_function}_tool = Tool.from_function(\n"
            f'    name="{tool_function}",\n'
            f'    func={tool_function},\n'
            f'    description="{purpose} {tool_input} {tool_output} {outcome}"\n'
            ")\n"
        )


        try:
            main_path = r"C:\Users\26389\OneDrive\shelby_new_ShenRui\main-ReAct-Agent.py"
            with open(main_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            lines.insert(48, import_statement + tool_definition)
            with open(main_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update main-ReAct-Agent.py: {e}")
            return

        # 更新 KGP.py 中的 tool_graph_to_chunks JSON 路径
        try:
            path = r"C:\Users\26389\OneDrive\shelby_new_ShenRui\KGP-part.py"
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            with open(path, "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip().startswith("chunks_docx = tool_graph_to_chunks("):
                        f.write(
                            f'chunks_docx = tool_graph_to_chunks('
                            f'input_json_file=r"{tool_graph}")\n'
                        )
                    else:
                        f.write(line)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update tool_graph_to_chunks.py: {e}")
            return

        messagebox.showinfo("Update Successful", "The tool has been updated successfully!")

    button_bar = tk.Frame(update_window, bg=BG_COLOR)
    button_bar.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 18))
    button_bar.columnconfigure(0, weight=1)

    ttk.Button(
        button_bar,
        text="Add this tool to the Tool kit",
        command=update_tool,
        style="AccentBlue.TButton"
    ).grid(row=0, column=0, sticky="ew")

# ====== 3. 主窗口 & ttk.Style ======
enable_windows_dpi_awareness()

root = tk.Tk()
root.title("Python Script Runner")

# 不做小数整体缩放，避免 Windows 对窗口进行二次缩放导致文字发虚。
# 输入框和输出框通过真实字号单独放大。
try:
    root.tk.call("tk", "scaling", 1.0)
except Exception:
    pass

root.geometry("1280x820")
root.resizable(True, True)
root.minsize(1180, 760)
root.configure(bg=BG_COLOR)
root.option_add("*TCombobox*Listbox.font", FONT_ENTRY)

style = ttk.Style(root)
style.theme_use("clam")

style.configure(
    "AccentGreen.TButton",
    font=FONT_ACCENT_BUTTON,
    foreground="white",
    background=ACCENT_GREEN,
    borderwidth=0,
    padding=(14, 8)
)
style.map(
    "AccentGreen.TButton",
    background=[("active", "#1BA9B6")]
)

style.configure(
    "AccentPurple.TButton",
    font=FONT_ACCENT_BUTTON,
    foreground=BG_COLOR,
    background=ACCENT_PURPLE,
    borderwidth=0,
    padding=(14, 8)
)
style.map(
    "AccentPurple.TButton",
    background=[("active", "#D79E2E")]
)

style.configure(
    "Default.TButton",
    font=FONT_BUTTON,
    foreground=BTN_DEFAULT_FG,
    background=BTN_DEFAULT_BG,
    borderwidth=0,
    padding=(12, 7)
)
style.map(
    "Default.TButton",
    background=[("active", "#223150")]
)

style.configure(
    "Modern.TEntry",
    fieldbackground=INPUT_BG,
    foreground=TEXT_PRIMARY,
    bordercolor=BORDER_COLOR,
    lightcolor=BORDER_COLOR,
    darkcolor=BORDER_COLOR,
    insertcolor=TEXT_PRIMARY,
    padding=(8, 6)
)

style.configure(
    "Modern.TCombobox",
    fieldbackground=INPUT_BG,
    background=INPUT_BG,
    foreground=TEXT_PRIMARY,
    arrowcolor=TEXT_PRIMARY,
    bordercolor=BORDER_COLOR,
    lightcolor=BORDER_COLOR,
    darkcolor=BORDER_COLOR,
    padding=(8, 6)
)

# ====== 4. 顶部区域 ======
header_frame = tk.Frame(
    root,
    bg=HEADER_BG,
    highlightbackground=BORDER_COLOR,
    highlightthickness=1,
    bd=0
)
header_frame.pack(fill="x", padx=18, pady=(16, 10))
header_frame.columnconfigure(0, weight=1)

create_header_icon_and_title(
    header_frame,
    r"C:\Users\26389\OneDrive\shelby_new_ShenRui\logo.png",
    HEADER_BG
)

# ====== 5. 主内容布局 ======
content_frame = tk.Frame(root, bg=BG_COLOR)
content_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))
content_frame.columnconfigure(0, weight=1)
content_frame.columnconfigure(1, weight=1)
content_frame.rowconfigure(0, weight=1)

left_card = create_card(content_frame, 0, 0, padx=(0, 10))
right_card = create_card(content_frame, 0, 1, padx=(10, 0))

# ====== 左侧：KGP 区块 ======
add_card_header(left_card, "Knowledge Graph-driven Planning (KGP)", ACCENT_GREEN)

add_section_title(left_card, "Task Input")
task_input_wrap = tk.Frame(left_card, bg=SURFACE_COLOR)
task_input_wrap.pack(fill="x", padx=20, pady=(0, 4))
task_input_wrap.columnconfigure(0, weight=1)

tk.Label(
    task_input_wrap,
    text="Please fill in the task for agents to response:",
    font=FONT_LABEL,
    fg=TEXT_SECONDARY,
    bg=SURFACE_COLOR,
    anchor="w",
    justify="left",
    wraplength=720
).grid(row=0, column=0, sticky="w", pady=(0, 3))

entry_task_input = tk.Text(
    task_input_wrap,
    height=1,
    width=58,
    font=FONT_ENTRY,
    bg=INPUT_BG,
    fg=TEXT_PRIMARY,
    insertbackground=TEXT_PRIMARY,
    highlightthickness=1,
    highlightbackground=BORDER_COLOR,
    relief="flat",
    wrap="word",
    padx=10,
    pady=5,
    spacing1=2,
    spacing3=2
)
entry_task_input.grid(row=1, column=0, sticky="ew")

add_section_title(left_card, "Set Parameters")
params_wrap = tk.Frame(left_card, bg=SURFACE_COLOR)
params_wrap.pack(fill="x", padx=20, pady=(0, 4))
params_wrap.columnconfigure(0, weight=2)
params_wrap.columnconfigure(1, weight=2)
params_wrap.columnconfigure(2, weight=3)

# Compact horizontal parameter layout: this removes the large vertical stack
# above the KGP output area while keeping all controls visible.
tk.Label(
    params_wrap,
    text="Select based LLM:",
    font=FONT_LABEL,
    fg=TEXT_SECONDARY,
    bg=SURFACE_COLOR,
    anchor="w",
    justify="left"
).grid(row=0, column=0, sticky="w", pady=(0, 3))

tk.Label(
    params_wrap,
    text="Temperature (0-1):",
    font=FONT_LABEL,
    fg=TEXT_SECONDARY,
    bg=SURFACE_COLOR
).grid(row=0, column=1, sticky="w", padx=(12, 0), pady=(0, 3))

tk.Label(
    params_wrap,
    text="OpenAI API key:",
    font=FONT_LABEL,
    fg=TEXT_SECONDARY,
    bg=SURFACE_COLOR
).grid(row=0, column=2, sticky="w", padx=(12, 0), pady=(0, 3))

llm_var_plan = tk.StringVar()
llm_dropdown_plan = ttk.Combobox(
    params_wrap,
    textvariable=llm_var_plan,
    values=["gpt-4", "gpt-4o", "gpt-5"],
    state="readonly",
    font=FONT_ENTRY,
    style="Modern.TCombobox"
)
llm_dropdown_plan.grid(row=1, column=0, sticky="ew", pady=(0, 6))
llm_dropdown_plan.current(0)

entry_temp_plan = ttk.Entry(params_wrap, font=FONT_ENTRY, style="Modern.TEntry")
entry_temp_plan.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(0, 6))

api_frame = tk.Frame(params_wrap, bg=SURFACE_COLOR)
api_frame.grid(row=1, column=2, sticky="ew", padx=(12, 0), pady=(0, 6))
api_frame.columnconfigure(0, weight=1)

entry_api_plan = ttk.Entry(api_frame, show="*", width=12, font=FONT_ENTRY, style="Modern.TEntry")
entry_api_plan.grid(row=0, column=0, sticky="ew")

toggle_button = ttk.Button(
    api_frame,
    text="Show key",
    command=toggle_api_visibility,
    style="Default.TButton"
)
toggle_button.grid(row=0, column=1, padx=(8, 0))

add_section_title(left_card, "Running Process of The KGP")
kgp_run_wrap = tk.Frame(left_card, bg=SURFACE_COLOR)
kgp_run_wrap.pack(fill="both", expand=True, padx=20, pady=(0, 20))
kgp_run_wrap.columnconfigure(0, weight=1)
kgp_run_wrap.rowconfigure(1, weight=1)

kgp_button_bar = tk.Frame(kgp_run_wrap, bg=SURFACE_COLOR)
kgp_button_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
kgp_button_bar.columnconfigure(0, weight=1)
kgp_button_bar.columnconfigure(1, weight=1)

ttk.Button(
    kgp_button_bar,
    text="Run KGP",
    style="AccentGreen.TButton",
    command=lambda: run_script(
        ["python", r"C:\Users\26389\OneDrive\shelby_new_ShenRui\KGP-part.py"],
        text_output_plan
    )
).grid(row=0, column=0, sticky="ew", padx=(0, 6))

ttk.Button(
    kgp_button_bar,
    text="Clear Output",
    style="Default.TButton",
    command=lambda: clear_console(text_output_plan)
).grid(row=0, column=1, sticky="ew", padx=(6, 0))

text_output_plan = tk.Text(kgp_run_wrap)
style_text_widget(text_output_plan, height=6)
text_output_plan.grid(row=1, column=0, sticky="nsew")

# ====== 右侧：ReAct Agent 区块 ======
add_card_header(right_card, "Reasoning and Action (ReAct) Agent", ACCENT_PURPLE)

add_section_title(right_card, "Set Parameters")
react_params_wrap = tk.Frame(right_card, bg=SURFACE_COLOR)
react_params_wrap.pack(fill="x", padx=20, pady=(0, 4))
react_params_wrap.columnconfigure(0, weight=1)
react_params_wrap.columnconfigure(1, weight=1)

tk.Label(
    react_params_wrap,
    text="Select based LLM:",
    font=FONT_LABEL,
    fg=TEXT_SECONDARY,
    bg=SURFACE_COLOR,
    anchor="w",
    justify="left"
).grid(row=0, column=0, sticky="w", pady=(0, 4))

tk.Label(
    react_params_wrap,
    text="LLM temperature (0-1):",
    font=FONT_LABEL,
    fg=TEXT_SECONDARY,
    bg=SURFACE_COLOR,
    anchor="w",
    justify="left"
).grid(row=0, column=1, sticky="w", padx=(12, 0), pady=(0, 4))

llm_var_exec = tk.StringVar()
llm_dropdown_exec = ttk.Combobox(
    react_params_wrap,
    textvariable=llm_var_exec,
    values=["gpt-4", "gpt-4o", "gpt-5"],
    state="readonly",
    font=FONT_ENTRY,
    style="Modern.TCombobox"
)
llm_dropdown_exec.grid(row=1, column=0, sticky="ew", pady=(0, 8))
llm_dropdown_exec.current(0)

entry_temp_exec = ttk.Entry(react_params_wrap, font=FONT_ENTRY, style="Modern.TEntry")
entry_temp_exec.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

# Static visual spacer: keeps the ReAct output aligned with KGP while avoiding
# the resize jitter caused by dynamic recalculation. The update button is placed
# in the middle of this reserved blank area, so the space is visually used
# instead of looking empty.
react_balance_spacer = tk.Frame(right_card, bg=SURFACE_COLOR, height=REACT_OUTPUT_TOP_SPACER + 44)
react_balance_spacer.pack(fill="x", padx=20, pady=(0, 4))
react_balance_spacer.pack_propagate(False)
react_balance_spacer.grid_propagate(False)
react_balance_spacer.columnconfigure(0, weight=1)
react_balance_spacer.columnconfigure(1, weight=5)
react_balance_spacer.columnconfigure(2, weight=1)
react_balance_spacer.rowconfigure(0, weight=1)

ttk.Button(
    react_balance_spacer,
    text="Update IIN-PRS Tool kit (optional)",
    style="Default.TButton",
    command=open_update_tool
).grid(row=0, column=1, sticky="ew")

add_section_title(right_card, "Running Process of The ReAct Agent")
react_run_wrap = tk.Frame(right_card, bg=SURFACE_COLOR)
react_run_wrap.pack(fill="both", expand=True, padx=20, pady=(0, 20))
react_run_wrap.columnconfigure(0, weight=1)
react_run_wrap.rowconfigure(1, weight=1)

react_button_bar = tk.Frame(react_run_wrap, bg=SURFACE_COLOR)
react_button_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
react_button_bar.columnconfigure(0, weight=1)
react_button_bar.columnconfigure(1, weight=1)

ttk.Button(
    react_button_bar,
    text="Run ReAct Agent",
    style="AccentPurple.TButton",
    command=lambda: None
).grid(row=0, column=0, sticky="ew", padx=(0, 6))

ttk.Button(
    react_button_bar,
    text="Clear Output",
    style="Default.TButton",
    command=lambda: clear_console(text_output_exec)
).grid(row=0, column=1, sticky="ew", padx=(6, 0))

text_output_exec = tk.Text(react_run_wrap)
style_text_widget(text_output_exec, height=6)
text_output_exec.grid(row=1, column=0, sticky="nsew")


# Keep the top edges of the two bottom output boxes aligned.
# This only adjusts the reserved visual spacer above the ReAct section.
def align_output_top_edges():
    try:
        root.update_idletasks()
        left_y = text_output_plan.winfo_rooty()
        right_y = text_output_exec.winfo_rooty()
        diff = left_y - right_y
        if abs(diff) > 2:
            current_height = react_balance_spacer.winfo_height()
            new_height = max(24, current_height + diff)
            if abs(new_height - current_height) > 1:
                react_balance_spacer.configure(height=new_height)
                root.after(80, align_output_top_edges)
    except Exception:
        pass

root.after(250, align_output_top_edges)
root.bind("<Configure>", lambda event: root.after_idle(align_output_top_edges))

# ====== 启动主循环 ======
root.mainloop()
