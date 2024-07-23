import cv2
import os

def camera():
    # Otevřít kameru připojenou přes USB
    cap = cv2.VideoCapture(1)

    # Nastavit rozměry výstupu
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Kontrola, zda kamera byla úspěšně otevřena
    if not cap.isOpened():
        print("Nelze otevřít kameru.")
        return

    # Počkej na stabilizaci obrazu
    print("Stabilizing camera...")
    for i in range(10):
        _, _ = cap.read()

    # Pořízení fotografie
    ret, frame = cap.read()

    # Uložení fotografie do souboru
    if ret:
        save = "path_to_input_image_or_video/photo.png"
        cv2.imwrite(save, frame)
        print("The photo was successfully taken.")
    else:
        print("Error when taking a photo.")

    # Uvolnění kamery a zavření okna
    cap.release()
    cv2.destroyAllWindows()

def delete_photo():
    file_path = "path_to_input_image_or_video/photo.png"
    # Ověření, zda soubor existuje
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print("Photo has been successfully deleted")
        except Exception as e:
            print(f'Chyba při odstraňování {file_path}. Důvod: {e}')
    else:
        print(f'Soubor neexistuje ve složce.')
'''
if __name__ == "__main__":
    camera()
'''