import cv2
import os

# Funkcja pomocnicza do wyświetlania obrazu
def show_image(title, img):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Wczytaj obraz szablonu RGB
rgb_template_img = cv2.imread('01.JPG')
show_image("Template RGB", rgb_template_img)

# Wczytaj obraz szablonu w skali szarości
template_img = cv2.imread('01.JPG', 0)
show_image("Template Grayscale", template_img)

# Zmień rozmiar obrazu szablonu
template_img_resize = cv2.resize(template_img, (750, 450))
show_image("Template Resized", template_img_resize)

# Rozmycie Gaussa
blur_template_img = cv2.GaussianBlur(template_img_resize, (3, 3), 0)
show_image("Template Blurred", blur_template_img)

# Progowanie adaptacyjne
template_adap_thresh = cv2.adaptiveThreshold(
    blur_template_img, 255,
    cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY, 15, 5
)
show_image("Template Adaptive Threshold", template_adap_thresh)

# Wczytaj testowy obraz RGB
rgb_test_img = cv2.imread('01_missing_hole_10.jpg')
show_image("Test RGB", rgb_test_img)

# Wczytaj testowy obraz w skali szarości
test_img = cv2.imread('01_missing_hole_10.jpg', 0)

# Zmień rozmiar testowego obrazu
test_img_resize = cv2.resize(test_img, (750, 450))
show_image("Test Resized", test_img_resize)

# Rozmycie Gaussa
blur_test_img = cv2.GaussianBlur(test_img_resize, (3, 3), 0)
show_image("Test Blurred", blur_test_img)

# Progowanie adaptacyjne dla obrazu testowego
test_adap_thresh = cv2.adaptiveThreshold(
    blur_test_img, 255,
    cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY, 15, 5
)
show_image("Test Adaptive Threshold", test_adap_thresh)

# Różnica obrazów
sub_img = cv2.subtract(template_adap_thresh, test_adap_thresh)
show_image("Subtracted Image", sub_img)

# Filtr medianowy
final_img = cv2.medianBlur(sub_img, 5)
show_image("Final Result", final_img)

# Detekcja konturów
cnts = cv2.findContours(final_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]

# Filtracja konturów
blobs = []
for cnt in cnts:
    if 0 < cv2.contourArea(cnt) < 300:
        blobs.append(cnt)

print("Number of defects in image:", len(blobs))
