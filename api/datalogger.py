import csv, os

# os - práce se souborama a složkama
#from socketIO_client import SocketIO, BaseNamespace


class DataLogger:
    def __init__(self, filename=None, kind='csv'):
        #self.socketIO = SocketIO('159.203.69.117', 3000)
        self.file = None
        self.kind = kind
        if filename is not None:
            directory = os.path.dirname(filename) #při získávání informací o umístění souboru nebo složky v cestě
            if not os.path.isdir(directory): #slouží k ověření, zda zadaná cesta (path) představuje existující složku (adresář)
                os.makedirs(directory) #slouží k vytvoření adresáře nebo více adresářů rekurzivně
            if self.kind == 'dat':
                filename += '.dat'
                self.file = open(filename, 'w')
            elif self.kind == 'csv':
                self.file = open(filename, 'wt')
                self.writer = csv.writer(self.file)

    def __call__(self, string):
        if self.file is not None:
            if self.kind == 'dat':
                self.file.write(string)
            elif self.kind == 'csv':
                self.writer.writerow(string)

        else:
            print (string)
            #self.socketIO.emit('log', {'raspID': 'a', 'log': string})

    def __del__(self):
        if self.file is not None:
            self.file.close()


'''''
Tento soubor obsahuje třídu nazvanou DataLogger, která slouží k zaznamenávání dat do souborů, 
a to buď ve formátu DAT nebo CSV. Níže je stručný popis některých částí kódu:

Inicializace třídy:
Konstruktor (__init__): Inicializuje objekt třídy. Přijímá argumenty filename (název souboru) 
a kind (typ souboru - buď 'dat' nebo 'csv'). Pokud je zadaný filename, vytvoří se soubor pro zápis do něj.

Otevírání souboru:
Pokud je zadaný filename, třída vytvoří soubor pro zápis. Pro CSV formát je také vytvořen objekt csv.writer.

Metoda __call__:
Tato metoda umožňuje objektu třídy být volán jako funkce. 
Přijímá řetězec (string) a zapisuje ho do souboru. Pokud soubor není otevřen, 
řetězec se vytiskne na standardní výstup.

Metoda __del__:
Tato metoda se volá, když je objekt třídy odstraněn. Zde slouží k uzavření otevřeného souboru.

Uzavření souboru:
V metodě __del__ je zajištěno, že soubor je uzavřen, pokud byl otevřen.

Použití SocketIO:
Kód obsahuje zakomentované části, které odkazují na modul SocketIO, 
který by pravděpodobně sloužil k odesílání dat na server pomocí SocketIO. 
Tyto části jsou v současné době zakomentované (# na začátku řádků), což znamená, že nejsou aktivní. 
Je možné, že tato funkcionalita byla zakomentována z důvodu nepotřebnosti nebo neaktivity.
Celkově tato třída poskytuje jednoduchý způsob pro zaznamenávání dat do souborů 
a může být rozšířena nebo upravena podle konkrétních potřeb.
'''