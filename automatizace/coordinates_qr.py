'''
podmínka pro qr kod 00, pokud je 00 nastav se jako ref bod
'''
import cv2
import numpy as np

def linesF():
    with open("data/qr_results_new.txt", "r") as file:
        return file.readlines()
    
def get_QR():
    llines = linesF()  # Call linesF to get the lines from the file
    QR_index = []  # List to store indices
    for lline in llines:
        parts = lline.split()
        index = int(parts[0])  # Convert the first part to an integer
        QR_index.append(index)  # Append the index to the list
    return QR_index  # Return the list of indices


def calibration(ref_point, xx,xy,xz, target_points):
    transformed_points = []

        # Známé souřadnice QR kódů ve skutečném světě (např. metrická soustava)
    real_world_points = np.float32([
        [0, 0],
        [121, 3],
        [123, 296],
        [-70, 295]
    ])
    
    # Detekované souřadnice QR kódů v obraze po posunutí kamery
    detected_points = np.float32([
        ref_point,
        xx,
        xy,
        xz
    ])
   
    # Vypočítáme homografickou matici
    H, status = cv2.findHomography(detected_points, real_world_points)

    # Zobrazíme vypočítanou matici
    
    #print(H)

    # Teď můžeme transformovat body z pohledu kamery zpět do souřadnic reálného světa
    # Například transformace jednoho bodu:
    for point in target_points:
        point_coordinates = np.array([point[1], point[2]], dtype='float32')
        point_coordinates = np.array([point_coordinates])
        

    # Transformace pomocí homografie
        transformed_point = cv2.perspectiveTransform(np.array([point_coordinates]), H)
        transformed_points.append([point[0], transformed_point[0][0][0], transformed_point[0][0][1]])
        print(transformed_points)
    # Transformace referenčního bodu
    ref_point_transp = np.array(ref_point, dtype='float32').reshape(1, 1, 2)
    ref_point_transp = cv2.perspectiveTransform(ref_point_transp, H)
    #print(ref_point_transp)
    '''
    # Transformace referenčního bodu
    print(xx)
    z = [1000, 534]
    xx_transp = np.array(z, dtype='float32').reshape(1, 1, 2)
    
    print(xx_transp)
    xx_transp = cv2.perspectiveTransform(xx_transp, H)
    print(xx_transp)
    '''
    return transformed_points, ref_point_transp[0][0]


def coordinates():
    target_points = []
    new_lines = []
    QR_values = []
    
    with open("data/qr_results.txt", 'r') as file:
        lines = file.readlines()
        for line in lines:
                # Rozdělení řádku na jednotlivé hodnoty
                values = line.split()
                # Výběr prvního čísla jako obsah qr kódu
                QR_all = values[0]
                
                if QR_all.isdigit():
                    QR = round(float(values[0]))
                    if QR != 0:
                        QR_values.append(QR) 
                        #print(QR_values)
                    if QR == 0:
                        ref_point = [float(values[1]),float(values[2])]
                        #print(ref_point)
                    else:
                        target_point = [round(QR),float(values[1]),float(values[2])]
                        target_points.append(target_point) 
                        #print(target_points)

                elif QR_all == "xx":
                    xx = [float(values[1]),float(values[2])]
                elif QR_all == "xy":
                    xy = [float(values[1]),float(values[2])]
                elif QR_all == "xz":
                    xz = [float(values[1]),float(values[2])]
                    
        transformed_points,ref_point_transp = calibration(ref_point, xx, xy, xz, target_points)
        k = len(transformed_points)
        #print(k)
        
        for i in range(k):
            # Získejte x a y z transformovaných bodů
            x_diff = transformed_points[i][1]
            y_diff = transformed_points[i][2]

            x_new = ((x_diff)+67)*2 #přepočet od pipety
            y_new = ((y_diff)-37)*2

        # Vytvoříme novou souřadnici
            new_point = [QR_values[i], x_new, y_new] #Kamera pravděpodobně otáčí souřadnice, 
            
            new_lines.append(f" {new_point[0]} {new_point[1]} {new_point[2]}")
            #print(new_lines)
        # Write the new points to a new file
        with open("data/qr_results_new.txt", 'w') as file:
            for line in new_lines:
                file.write(line + "\n")

        print("Nové souřadnice byly uloženy do souboru data/qr_results_new.txt")
        #QR_index = get_QR()  # Call to get all indices
        #print( QR_index) 


