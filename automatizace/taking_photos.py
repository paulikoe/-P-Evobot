import cv2
import os

def camera_prepare(self):
    # Otevřít kameru připojenou přes USB
    cap = cv2.VideoCapture(1) # for USB camera
    #cap = cv2.VideoCapture(0)

    # Nastavit rozměry výstupu
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    '''
    # Kontrola, zda kamera byla úspěšně otevřena
    if not cap.isOpened():
        print("Nelze otevřít kameru.")
        return
    '''
    # Počkej na stabilizaci obrazu
    print("Stabilizing camera...")
    for i in range(2):
        _, _ = cap.read()

    self.cap = cap  # Uložení objektu cap do atributu instance
    self.camera_ready.set()  # Signalizace, že kamera je připravena

    return cap

def camera_photo(self):
    """Pořízení fotografie a zobrazení výsledku"""
    ret, frame = self.cap.read()

    if ret:
        save = "path_to_input_image_or_video/photo.png"
        cv2.imwrite(save, frame)
        self.show("The photo was successfully taken.")
    else:
        self.show("Error when taking a photo. The image from the previous launch will be used.")

    self.cap.release()  # Uvolnění kamery
    cv2.destroyAllWindows()


def camera(self):
    # Otevřít kameru připojenou přes USB
    cap = cv2.VideoCapture(1)

    # Nastavit rozměry výstupu
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    '''
    # Kontrola, zda kamera byla úspěšně otevřena
    if not cap.isOpened():
        print("Nelze otevřít kameru.")
        return
    '''
    # Počkej na stabilizaci obrazu
    print("Stabilizing camera...")
    for i in range(2):
        _, _ = cap.read()
    
    # Pořízení fotografie
    ret, frame = cap.read()

    # Uložení fotografie do souboru
    if ret:
        save = "path_to_input_image_or_video/photo.png"
        cv2.imwrite(save, frame)

        #print("The photo was successfully taken.")
        self.show("The photo was successfully taken.")
    else:
        #print("Error when taking a photo.")
        self.show("Error when taking a photo. The image from the previous launch will be used.")

    # Uvolnění kamery a zavření okna
    cap.release()
    cv2.destroyAllWindows()


