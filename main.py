import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

MAX_WIDTH = 750
MAX_HEIGHT = 450

def resize_to_fit(image):
    height, width = image.shape[:2]
    scale = min(MAX_WIDTH / width, MAX_HEIGHT / height, 1.0)
    new_size = (int(width * scale), int(height * scale))
    return cv2.resize(image, new_size)

def cv2_to_image_tk(cv_img):
    cv_img = resize_to_fit(cv_img)
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    return ImageTk.PhotoImage(img)

def cv2_gray_to_image_tk(cv_img):
    cv_img = resize_to_fit(cv_img)
    img = Image.fromarray(cv_img)
    return ImageTk.PhotoImage(img)

class ImageProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Porównywanie obrazów PCB")
        self.root.geometry("1000x700")

        self.template_path = None
        self.test_path = None

        self.images = {}      # do wyświetlania (ImageTk)
        self.cv2_images = {}  # do zapisu (cv2)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.controls = tk.Frame(self.root)
        self.controls.pack(pady=10)

        self.label_result = tk.Label(self.root, text="Wynik: brak danych", font=("Arial", 14))
        self.label_result.pack(pady=10)

        self.btn_load_template = tk.Button(self.controls, text="Wczytaj szablon", command=self.load_template)
        self.btn_load_template.grid(row=0, column=0, padx=10)

        self.btn_load_test = tk.Button(self.controls, text="Wczytaj testowy", command=self.load_test)
        self.btn_load_test.grid(row=0, column=1, padx=10)

        self.btn_save = tk.Button(self.controls, text="Zapisz obrazy", command=self.save_images)
        self.btn_save.grid(row=0, column=2, padx=10)

    def load_template(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if path:
            self.template_path = path
            self.try_process_images()

    def load_test(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if path:
            self.test_path = path
            self.try_process_images()

    def try_process_images(self):
        if self.template_path and self.test_path:
            self.process_images(self.template_path, self.test_path)

    def process_images(self, template_path, test_path):
        self.images.clear()
        self.cv2_images.clear()

        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        # Template RGB
        rgb_template_img = cv2.imread(template_path)
        self.cv2_images['Template RGB'] = resize_to_fit(rgb_template_img)
        self.images['Template RGB'] = cv2_to_image_tk(rgb_template_img)

        # Template grayscale
        template_img = cv2.imread(template_path, 0)
        self.cv2_images['Template Grayscale'] = resize_to_fit(template_img)
        self.images['Template Grayscale'] = cv2_gray_to_image_tk(template_img)

        # Resized
        template_img_resize = resize_to_fit(template_img)
        self.cv2_images['Template Resized'] = template_img_resize
        self.images['Template Resized'] = cv2_gray_to_image_tk(template_img_resize)

        # Blurred
        blur_template_img = cv2.GaussianBlur(template_img_resize, (3, 3), 0)
        self.cv2_images['Template Blurred'] = blur_template_img
        self.images['Template Blurred'] = cv2_gray_to_image_tk(blur_template_img)

        # Adaptive threshold
        template_adap_thresh = cv2.adaptiveThreshold(
            blur_template_img, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 15, 5
        )
        self.cv2_images['Template Adaptive Threshold'] = template_adap_thresh
        self.images['Template Adaptive Threshold'] = cv2_gray_to_image_tk(template_adap_thresh)

        # Test RGB
        rgb_test_img = cv2.imread(test_path)
        self.cv2_images['Test RGB'] = resize_to_fit(rgb_test_img)
        self.images['Test RGB'] = cv2_to_image_tk(rgb_test_img)

        # Test grayscale
        test_img = cv2.imread(test_path, 0)
        test_img_resize = resize_to_fit(test_img)
        self.cv2_images['Test Resized'] = test_img_resize
        self.images['Test Resized'] = cv2_gray_to_image_tk(test_img_resize)

        # Test blurred
        blur_test_img = cv2.GaussianBlur(test_img_resize, (3, 3), 0)
        self.cv2_images['Test Blurred'] = blur_test_img
        self.images['Test Blurred'] = cv2_gray_to_image_tk(blur_test_img)

        # Test adaptive threshold
        test_adap_thresh = cv2.adaptiveThreshold(
            blur_test_img, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 15, 5
        )
        self.cv2_images['Test Adaptive Threshold'] = test_adap_thresh
        self.images['Test Adaptive Threshold'] = cv2_gray_to_image_tk(test_adap_thresh)

        # Subtracted image
        sub_img = cv2.subtract(template_adap_thresh, test_adap_thresh)
        self.cv2_images['Subtracted Image'] = sub_img
        self.images['Subtracted Image'] = cv2_gray_to_image_tk(sub_img)

        # Final result (median blur)
        final_img = cv2.medianBlur(sub_img, 5)
        self.cv2_images['Final Result'] = final_img
        self.images['Final Result'] = cv2_gray_to_image_tk(final_img)

        # Defect detection
        cnts = cv2.findContours(final_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
        blobs = [cnt for cnt in cnts if 0 < cv2.contourArea(cnt) < 300]
        defect_count = len(blobs)

        self.label_result.config(text=f"Liczba defektów: {defect_count}")

        for name, img in self.images.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)

            label = tk.Label(frame, image=img)
            label.pack(padx=10, pady=10)

            frame.img = img  # Zapobiega usunięciu z pamięci

    def save_images(self):
        if not self.cv2_images:
            messagebox.showwarning("Brak obrazów", "Najpierw wczytaj i przetwórz obrazy.")
            return

        folder = filedialog.askdirectory(title="Wybierz folder do zapisu obrazów")
        if not folder:
            return

        for name, img in self.cv2_images.items():
            safe_name = name.replace(" ", "_").lower() + ".png"
            save_path = f"{folder}/{safe_name}"
            cv2.imwrite(save_path, img)

        messagebox.showinfo("Zapisano", f"Obrazy zostały zapisane do folderu:\n{folder}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop()
