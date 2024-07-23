from qreader import QReader
import os
from PIL import Image
import cv2

def process_file():
    
    # Použití funkce
    file_path = 'yolov5/runs/detect\exp/labels/photo.txt'
    image_path = "path_to_input_image_or_video/photo.png"
    output_path = "data/qr_results.txt" 

    crop_size = 50  # Polovina šířky a výšky oříznutí

    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(output_path, 'w') as output_file:
    # Otevření souboru
    
    # Pro každý řádek ve souboru
        for line in lines:
            # Rozdělení řádku na jednotlivé hodnoty
            values = line.split()
            # Výběr druhého a třetího čísla jako souřadnic středu
            x_center = float(values[1]) * 1920
            y_center = float(values[2]) * 1080

            # Výpis středu rámce
            #print("Center:", x_center, y_center)

            # Výpočet oblasti oříznutí
            left = x_center - crop_size
            right = x_center + crop_size
            top = y_center - crop_size
            bottom = y_center + crop_size
            
            # Otevření obrázku
            image = Image.open(image_path)
            
            # Oříznutí obrázku na základě vypočtených souřadnic
            cropped_image = image.crop((left, top, right, bottom))
            cropped_image_path = 'cropped_image.jpg'
            cropped_image.save(cropped_image_path)

            # Načtení oříznutého obrázku pro detekci QR kódů
            img = cv2.imread(cropped_image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Detekce a dekódování QR kódů v obrázku
            detector = QReader()
            QRs = detector.detect_and_decode(image=img)
            
            # Výpis výsledků
            for QR in QRs:
                result_line = f"{QR} {x_center} {y_center}\n"
                output_file.write(result_line)
            
            # Odstranění dočasného souboru
            os.remove(cropped_image_path)


