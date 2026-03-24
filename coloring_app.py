import tkinter as tk
from tkinter import colorchooser, messagebox
import math

class ColoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Vẽ và Tô Màu")
        self.root.geometry("900x600")
        
        # Frame cho công cụ
        self.toolbar = tk.Frame(self.root, bg="lightgray", height=60)
        self.toolbar.pack(fill="x", pady=5, padx=5)
        
        # Nút chọn công cụ
        tk.Label(self.toolbar, text="Công cụ:", bg="lightgray").pack(side="left", padx=5)
        
        self.tool_var = tk.StringVar(value="draw")
        tk.Radiobutton(
            self.toolbar, text="✏️ Vẽ hình tròn", 
            variable=self.tool_var, value="draw",
            bg="lightgray"
        ).pack(side="left", padx=5)
        
        tk.Radiobutton(
            self.toolbar, text="🎨 Tô màu", 
            variable=self.tool_var, value="paint",
            bg="lightgray"
        ).pack(side="left", padx=5)
        
        # Nút chọn màu
        tk.Label(self.toolbar, text="Màu:", bg="lightgray").pack(side="left", padx=10)
        
        self.color_btn = tk.Button(
            self.toolbar, 
            text="   ",
            bg="white",
            command=self.choose_color,
            width=5,
            height=2
        )
        self.color_btn.pack(side="left", padx=5)
        
        self.current_color = "white"
        
        # Nút xóa tất cả
        tk.Button(
            self.toolbar,
            text="🗑️ Xóa tất cả",
            command=self.clear_canvas,
            bg="lightcoral"
        ).pack(side="left", padx=5)
        
        # Canvas vẽ
        self.canvas = tk.Canvas(
            self.root, 
            bg="white", 
            cursor="crosshair",
            relief="sunken",
            bd=2
        )
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Thùng rác
        self.trash_x = 800
        self.trash_y = 500
        self.trash_width = 60
        self.trash_height = 60
        self.trash_id = self.canvas.create_rectangle(
            self.trash_x, self.trash_y,
            self.trash_x + self.trash_width, self.trash_y + self.trash_height,
            fill="lightcoral", outline="black", width=2
        )
        self.canvas.create_text(
            self.trash_x + self.trash_width // 2, self.trash_y + self.trash_height // 2,
            text="🗑️", font=("Arial", 20)
        )
        
        # Bind sự kiện
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Danh sách các đối tượng hình tròn
        self.circles = []
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.preview_circle = None
        self.selected_circle = None
        self.drag_start = None
        
        # Gợi ý
        self.info_label = tk.Label(
            self.root,
            text="💡 Vẽ: Click và kéo để vẽ hình tròn | Tô màu: Click để tô màu hình tròn | Kéo hình tròn vào 🗑️ để xóa",
            bg="lightyellow",
            padx=10,
            pady=5
        )
        self.info_label.pack(fill="x")
    
    def get_circle_at(self, x, y):
        """Tìm hình tròn tại vị trí (x, y)"""
        for circle in reversed(self.circles):
            distance = math.sqrt(
                (x - circle["x"])**2 + 
                (y - circle["y"])**2
            )
            if distance <= circle["radius"]:
                return circle
        return None
    
    def choose_color(self):
        """Chọn màu"""
        color = colorchooser.askcolor(color=self.current_color)
        if color[1]:
            self.current_color = color[1]
            self.color_btn.config(bg=self.current_color)
    
    def on_canvas_click(self, event):
        """Xử lý khi click trên canvas"""
        # Kiểm tra xem có click vào hình tròn không
        self.selected_circle = self.get_circle_at(event.x, event.y)
        
        if self.selected_circle:
            # Bắt đầu kéo hình tròn
            self.drag_start = (event.x, event.y)
            return
        
        self.drag_start = None
        
        if self.tool_var.get() == "draw":
            # Vẽ hình tròn
            self.start_x = event.x
            self.start_y = event.y
            self.drawing = True
        else:
            # Tô màu
            self.paint_bucket(event.x, event.y)
    
    def on_canvas_drag(self, event):
        """Xử lý khi kéo trên canvas"""
        if self.selected_circle and self.drag_start:
            # Di chuyển hình tròn
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            
            self.selected_circle["x"] += dx
            self.selected_circle["y"] += dy
            
            radius = self.selected_circle["radius"]
            
            # Cập nhật vị trí trên canvas
            self.canvas.coords(
                self.selected_circle["id"],
                self.selected_circle["x"] - radius,
                self.selected_circle["y"] - radius,
                self.selected_circle["x"] + radius,
                self.selected_circle["y"] + radius
            )
            
            self.drag_start = (event.x, event.y)
            return
        
        if self.tool_var.get() == "draw" and self.drawing:
            # Xóa hình tròn xem trước cũ
            if self.preview_circle:
                self.canvas.delete(self.preview_circle)
            
            # Tính bán kính
            radius = math.sqrt(
                (event.x - self.start_x)**2 + 
                (event.y - self.start_y)**2
            )
            
            # Vẽ hình tròn xem trước
            self.preview_circle = self.canvas.create_oval(
                self.start_x - radius,
                self.start_y - radius,
                self.start_x + radius,
                self.start_y + radius,
                fill=self.current_color,
                outline="black",
                width=2
            )
    
    def on_canvas_release(self, event):
        """Xử lý khi thả chuột"""
        if self.selected_circle:
            # Kiểm tra xem có kéo vào thùng rác không
            if (self.trash_x <= event.x <= self.trash_x + self.trash_width and
                self.trash_y <= event.y <= self.trash_y + self.trash_height):
                # Xóa hình tròn
                self.canvas.delete(self.selected_circle["id"])
                self.circles.remove(self.selected_circle)
            
            self.selected_circle = None
            return
        
        if self.tool_var.get() == "draw" and self.drawing:
            # Tính bán kính cuối cùng
            radius = math.sqrt(
                (event.x - self.start_x)**2 + 
                (event.y - self.start_y)**2
            )
            
            if radius > 5:  # Chỉ tạo hình tròn nếu bán kính >= 5
                circle_id = self.canvas.create_oval(
                    self.start_x - radius,
                    self.start_y - radius,
                    self.start_x + radius,
                    self.start_y + radius,
                    fill=self.current_color,
                    outline="black",
                    width=2
                )
                
                # Lưu thông tin hình tròn
                self.circles.append({
                    "id": circle_id,
                    "x": self.start_x,
                    "y": self.start_y,
                    "radius": radius,
                    "color": self.current_color
                })
            
            # Xóa preview
            if self.preview_circle:
                self.canvas.delete(self.preview_circle)
                self.preview_circle = None
            
            self.drawing = False
    
    def paint_bucket(self, x, y):
        """Thuật toán tô màu (flood fill)"""
        # Kiểm tra xem điểm click có nằm trong hình tròn nào không
        for circle in self.circles:
            distance = math.sqrt(
                (x - circle["x"])**2 + 
                (y - circle["y"])**2
            )
            
            if distance <= circle["radius"]:
                # Tô màu hình tròn
                old_color = circle["color"]
                circle["color"] = self.current_color
                self.canvas.itemconfig(circle["id"], fill=self.current_color)
                messagebox.showinfo(
                    "Tô màu",
                    f"Đổi màu từ {old_color} sang {self.current_color}"
                )
                return
        
        messagebox.showwarning(
            "Thông báo",
            "Bạn chưa click vào hình tròn nào!"
        )
    
    def clear_canvas(self):
        """Xóa tất cả hình tròn"""
        result = messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa tất cả hình tròn?"
        )
        
        if result:
            self.canvas.delete("all")
            self.circles = []
            self.preview_circle = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ColoringApp(root)
    root.mainloop()
