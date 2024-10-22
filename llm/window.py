import tkinter as tk
from recognizer import Recognizer
import threading
from llm import LLM
from utils import time_logger, get_green_logger

logger = get_green_logger()


class ImprovedFloatingWindow:
    def __init__(self, master):
        logger.info("Initializing ImprovedFloatingWindow")
        self.master = master
        self.master.overrideredirect(True)  # 移除窗口边框
        self.master.attributes("-alpha", 0.7)  # 设置透明度
        self.master.attributes("-topmost", True)  # 窗口置顶
        self.master.geometry("500x300+200+200")  # 设置初始大小和位置为 500x300

        logger.info("Creating Recognizer instance")
        self.recognizer = Recognizer(
            callback=self.update_text, endpoint_callback=self.handle_endpoint
        )
        logger.info("Creating LLM instance")
        self.llm = LLM(callback=self.update_text_response)

        # 创建主框架
        self.main_frame = tk.Frame(self.master, bg="black")
        self.main_frame.pack(expand=True, fill="both")

        # 创建标题栏
        self.title_bar = tk.Frame(self.main_frame, bg="gray", height=20)
        self.title_bar.pack(fill="x")

        # 创建关闭按钮
        self.close_button = tk.Button(
            self.title_bar,
            text="X",
            command=self.master.quit,
            bg="red",
            fg="white",
            bd=0,
            padx=5,
            pady=2,
        )
        self.close_button.pack(side="right")

        # 创建Text控件用于显示文本
        self.text_widget = tk.Text(
            self.main_frame,
            wrap=tk.WORD,  # 启用自动换行
            bg="black",
            fg="white",
            font=("Arial", 12),
            relief=tk.FLAT,  # 移除边框
        )
        self.text_widget.pack(expand=True, fill="both")
        self.text_widget.insert(tk.END, "Waiting for you, sir")
        self.text_widget.config(state=tk.DISABLED)  # 使文本不可编辑

        # 创建标签用于显示端点检测信息
        self.endpoint_label = tk.Label(
            self.main_frame,
            text="",
            bg="black",
            fg="yellow",
            font=("Arial", 10),
        )
        self.endpoint_label.pack(side="bottom", fill="x")

        # 绑定鼠标事件
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_move)

        # 绑定调整大小的事件
        self.master.bind("<Button-1>", self.start_resize)
        self.master.bind("<B1-Motion>", self.on_resize)
        self.master.bind("<Configure>", self.on_window_resize)

        # 用于存储鼠标位置和窗口大小
        self.x = 0
        self.y = 0
        self.start_width = 0
        self.start_height = 0

        logger.info("Starting recognition")
        self.start_recognition()

        self.current_text = "Waiting for you, sir"
        logger.info("ImprovedFloatingWindow initialization complete")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.x = event.x
        self.y = event.y
        self.start_width = self.master.winfo_width()
        self.start_height = self.master.winfo_height()

    def on_resize(self, event):
        if (
            self.master.winfo_width() - event.x <= 10
            and self.master.winfo_height() - event.y <= 10
        ):
            width = max(self.start_width + event.x - self.x, 300)  # 最小宽度为300
            height = max(self.start_height + event.y - self.y, 200)  # 最小高度为200
            self.master.geometry(f"{width}x{height}")

    def on_window_resize(self, event):
        # 当窗口大小改变时，更新文本显示
        self.update_text(self.current_text)

    def update_text(self, text):
        self.current_text = text
        self.master.after(0, lambda: self._update_text_widget(text))

    def update_text_response(self, text):
        self.master.after(0, lambda: self._update_text_widget(text))

    def _update_text_widget(self, text):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, text)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)  # 滚动到最新内容

    def handle_endpoint(self):
        # 更新面板回复
        self.master.after(
            0, lambda: self._update_text_widget("assistant: 正在理解信息...")
        )

        # 在新线程中调用 LLM 的 chat 方法
        threading.Thread(
            target=self.process_llm_response, args=(self.current_text,), daemon=True
        ).start()

    def process_llm_response(self, text):
        # 调用 LLM 的 chat 方法

        self.llm.chat(text)
        # LLM 的回调函数会自动更新界面显示

    def start_recognition(self):
        threading.Thread(target=self.recognizer.online_recognize, daemon=True).start()


if __name__ == "__main__":
    logger.info("Starting main application")
    root = tk.Tk()
    app = ImprovedFloatingWindow(root)
    logger.info("Entering main loop")
    root.mainloop()
