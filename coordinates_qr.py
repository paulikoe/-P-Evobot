'''
podmínka pro qr kod 00, pokud je 00 nastav se jako ref bod
'''
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
            
                QR = round(float(values[0]))
                QR_values.append(QR) 
        
                if QR == 00:
                    ref_point = [float(values[1]),float(values[2])]
                    #print(ref_point)
                else:
                    target_point = [round(QR),float(values[1]),float(values[2])]
                    target_points.append(target_point) 
                    #print(target_points)
                
        
        k = len(target_points)

        for i in range(k):
        
            x_diff = target_points[i][1] - ref_point[0]
            y_diff = target_points[i][2] - ref_point[1]
            
            x_new = abs(x_diff * 0.26)
            y_new = abs(y_diff * 0.26)
            

        # Vytvoříme novou souřadnici
            new_point = [QR_values[i],x_new, y_new]
            
            
            new_lines.append(f" {new_point[0]} {new_point[1]} {new_point[2]}")
            #print(new_lines)
        # Write the new points to a new file
        with open("data/qr_results_new.txt", 'w') as file:
            for line in new_lines:
                file.write(line + "\n")

        print("Nové souřadnice byly uloženy do souboru data/qr_results_new.txt")

        #print("Nové souřadnice jsou:", new_point)

'''

# Referenční souřadnice
ref_point = [1482.4992, 667.0004399999999]


# Získané souřadnice, které chceme upravit
target_point = [1011.00096, 667.50048]

# Odečteme hodnoty referenčního bodu od cílového bodu
x_diff = target_point[0] - ref_point[0]
y_diff = target_point[1] - ref_point[1]

# Vynásobíme rozdíly hodnotou 0.26
x_new = abs(x_diff * 0.26)
y_new = abs(y_diff * 0.26)

# Vytvoříme novou souřadnici
new_point = [x_new, y_new]

print("Nové souřadnice jsou:", new_point)
'''