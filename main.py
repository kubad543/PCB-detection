import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


MAX_WIDTH = 750
MAX_HEIGHT = 450


def resize_to_fit(image):
    height, width = image.shape[:2]
    scale = min(MAX_WIDTH / width, MAX_HEIGHT / height, 1.0)  # Nie powiększaj obrazów
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


def prepare_images():
    images = {}

    # Wczytanie i przetwarzanie obrazu szablonu
    rgb_template_img = cv2.imread('01.JPG')
    images['Template RGB'] = cv2_to_image_tk(rgb_template_img)

    template_img = cv2.imread('01.JPG', 0)
    images['Template Grayscale'] = cv2_gray_to_image_tk(template_img)

    template_img_resize = resize_to_fit(template_img)
    images['Template Resized'] = cv2_gray_to_image_tk(template_img_resize)

    blur_template_img = cv2.GaussianBlur(template_img_resize, (3, 3), 0)
    images['Template Blurred'] = cv2_gray_to_image_tk(blur_template_img)

    template_adap_thresh = cv2.adaptiveThreshold(
        blur_template_img, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 15, 5
    )
    images['Template Adaptive Threshold'] = cv2_gray_to_image_tk(template_adap_thresh)

    # Wczytanie i przetwarzanie obrazu testowego
    rgb_test_img = cv2.imread('01_missing_hole_10.jpg')
    images['Test RGB'] = cv2_to_image_tk(rgb_test_img)

    test_img = cv2.imread('01_missing_hole_10.jpg', 0)
    test_img_resize = resize_to_fit(test_img)
    images['Test Resized'] = cv2_gray_to_image_tk(test_img_resize)

    blur_test_img = cv2.GaussianBlur(test_img_resize, (3, 3), 0)
    images['Test Blurred'] = cv2_gray_to_image_tk(blur_test_img)

    test_adap_thresh = cv2.adaptiveThreshold(
        blur_test_img, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 15, 5
    )
    images['Test Adaptive Threshold'] = cv2_gray_to_image_tk(test_adap_thresh)

    sub_img = cv2.subtract(template_adap_thresh, test_adap_thresh)
    images['Subtracted Image'] = cv2_gray_to_image_tk(sub_img)

    final_img = cv2.medianBlur(sub_img, 5)
    images['Final Result'] = cv2_gray_to_image_tk(final_img)

    # Detekcja konturów
    cnts = cv2.findContours(final_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
    blobs = [cnt for cnt in cnts if 0 < cv2.contourArea(cnt) < 300]
    defect_count = len(blobs)

    return images, defect_count


def create_gui(root, images, defect_count):
    root.title("Image Processing GUI")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    for name, img in images.items():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=name)

        label = tk.Label(frame, image=img)
        label.pack(padx=10, pady=10)

        # Przypisanie obrazka do ramki, aby nie został usunięty przez garbage collector
        frame.img = img

    label = tk.Label(root, text=f"Liczba defektów: {defect_count}", font=("Arial", 16))
    label.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ukryj okno podczas przygotowania obrazów

    images, defect_count = prepare_images()

    root.deiconify()  # Odsłoń okno
    create_gui(root, images, defect_count)
