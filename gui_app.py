import threading
import queue
import customtkinter as ctk
from scraper import scrape_baidu_maps

# ==========================================
# 💎 UI 主题与全局设定
# ==========================================
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class LeadMagnetApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LeadMagnet Pro 智能客源挖掘系统 - 引擎: 百度地图")
        self.geometry("950x650")
        self.minsize(800, 500)
        
        # 消息通信队列
        self.log_queue = queue.Queue()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 左侧控制面板 (Left Panel)
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.left_frame, text="LeadMagnet Pro", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 10))
        
        self.sub_label = ctk.CTkLabel(self.left_frame, text="0成本精准自动化拓客", text_color="gray", font=ctk.CTkFont(size=12))
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 40))

        # 关键词输入框
        self.query_label = ctk.CTkLabel(self.left_frame, text="🔍 搜索关键词 (地域+行业):", anchor="w")
        self.query_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.query_entry = ctk.CTkEntry(self.left_frame, placeholder_text="例如：杭州市 咖啡店")
        self.query_entry.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")

        # 数量输入框
        self.num_label = ctk.CTkLabel(self.left_frame, text="📊 目标采集条数:", anchor="w")
        self.num_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.num_entry = ctk.CTkEntry(self.left_frame, placeholder_text="默认20条")
        self.num_entry.grid(row=5, column=0, padx=20, pady=(5, 20), sticky="nwe")

        # 底部开始按钮
        self.start_button = ctk.CTkButton(self.left_frame, text="🚀 立即开始采集", fg_color="#1f538d", hover_color="#14375d", font=ctk.CTkFont(size=15, weight="bold"), height=45, command=self.start_scraping)
        self.start_button.grid(row=6, column=0, padx=20, pady=40, sticky="ew")

        # ==========================================
        # 右侧日志面板 (Right Panel)
        # ==========================================
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.log_title = ctk.CTkLabel(self.right_frame, text="💻 系统运行日志 (实时数据获取)", font=ctk.CTkFont(size=16, weight="bold"))
        self.log_title.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # 终端样式文本框
        self.log_textbox = ctk.CTkTextbox(self.right_frame, fg_color="#1e1e1e", text_color="#00FF00", font=ctk.CTkFont(family="Consolas", size=13))
        self.log_textbox.grid(row=1, column=0, sticky="nsew")
        
        self.log_textbox.insert("0.0", "欢迎使用 LeadMagnet Pro.\n准备就绪。请输入条件后点击开始...\n")
        
        # 启动 UI 事件循环刷新队列
        self.check_queue()

    def append_log(self, msg):
        """将日志放入队列，确保线程安全"""
        self.log_queue.put(msg)

    def check_queue(self):
        """定时从队列中提取并显示日志"""
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_textbox.insert("end", msg + "\n")
            self.log_textbox.see("end")  # 自动滚动到底部
        self.after(100, self.check_queue)

    def start_scraping(self):
        query = self.query_entry.get().strip()
        num_str = self.num_entry.get().strip()
        
        if not query:
            self.append_log("❌ 请输入关键词！例如: '成都市 装修公司'")
            return
            
        num = 20
        if num_str:
            try:
                num = int(num_str)
            except ValueError:
                self.append_log("⚠️ 采集数目必须是整数，将默认采用 20。")
        
        self.start_button.configure(state="disabled", text="⏳ 正在采集中...")
        self.log_textbox.delete("0.0", "end")
        
        # 启动线程执行爬虫操作，防止阻塞 GUI
        threading.Thread(target=self.run_scraper_task, args=(query, num), daemon=True).start()
        
    def run_scraper_task(self, query, num):
        try:
            scrape_baidu_maps(search_query=query, total_to_scrape=num, log_callback=self.append_log)
        except Exception as e:
            self.append_log(f"🔥 程序崩溃: {str(e)}")
        finally:
            # 任务执行完毕，恢复按钮状态
            self.append_log("\n👉 本次任务已结束。请前往 output 文件夹查看生成的 Excel 表单。")
            self.start_button.configure(state="normal", text="🚀 再次开始采集")

if __name__ == "__main__":
    app = LeadMagnetApp()
    app.mainloop()
