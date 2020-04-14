import re
from capstone import *
from binascii import unhexlify
from elftools.elf.elffile import *


class Disassembler:
    def __init__(self, file):
        self.file = file

    def __str__(self):
        return "\nClass: Disassembler" \
               "\nConstructor: __init__(file path)" \
               "\nFunctions: [hexdump(), printHexdump(), " \
               "getSections(), disAssembler(), getStrings(), searchString()]"

    def hexdump(self):
        """
        Questa funzione serve per ricavare indirizzi di memoria, valori esadecimali e
        stringhe nel file dato come parametro nel costruttore.
        Ritorna:
        1 dizionario: indirizzo memoria, valori esadecimali, valori asscii
        1 lista: solo valori esadecimali
        """

        address = 0
        hexcode, asciicode = "", ""
        hxdmp = {}
        onlyhxdmp = []

        with open(self.file, 'rb') as bytesinfile:
            for row in bytesinfile:
                for c in row:
                    # Ogni byte viene rappresentato con 2 caratteri Es: 6F A1 0C
                    hexcode += '{:02x}'.format(c)

                    # controllo e aggiungo solo i caratteri ascii stampabili
                    asciicode += chr(c) if 32 <= c < 127 else "."

                    address += 1

                    # Ogni volta che arrivo ad un multiplo di 16 creo un record nel dizionario
                    # L'indirizzo fa da chiave e gli altri valore vengono inseriti in una lista
                    if not address % 16:
                        # onlyhxdmp.append(hex)
                        onlyhxdmp.append(hexcode)
                        hxdmp['0x{:08X}'.format(address - 16)] = [hexcode, asciicode]
                        hexcode, asciicode = "", ""

        return hxdmp, onlyhxdmp

    def getHexdump(self, byteslen='304', ref_address=""):
        """
        Questa funzione serve per dare una formattazione al hexdump del file
        Come parametri puo ricevere il numero di bytes da ritornare e l'indirizzo da cui partire.
        Ritorna: 1 lista
        """
        hexcode = self.hexdump()[0]
        # Si no se eespecifica cuantos bytes imprimir se imprime todo
        byteslen = len(hexcode) * 16 if len(byteslen) == 0 else int(byteslen)

        # Serve per ottenere il numero di records da ritornare
        hexrange = (byteslen // 16) + (1 if (byteslen % 16) else 0) if byteslen else len(hexcode)

        result = []

        for i in range(hexrange):
            # Prendo e formatto l'indirizzo di memoria della section .text (Entry point)
            # Questa seccione è quella che contiene tutto il codice del programma
            # Di default parto da quel indirizzo a me no che non venga specificato un altro
            current_address = '0x{:08X}'.format(self.getSections()[".text"])
            current_index = list(hexcode.keys()).index(current_address if len(ref_address) == 0 else ref_address)
            address = list(hexcode.keys())[current_index:][i]

            hexout = ""
            asciiout = ""

            for j in range(0, (16 if byteslen <= 0 else byteslen) * 2, 2):
                hexout += hexcode[address][0][j:j + 2]

                try:
                    asciiout += hexcode[address][1][j - (j // 2)]
                except IndexError:
                    pass

            # Costruisco la stringa dei valori esadecimali facendo gruppi di 4 in 4. Es: aaaa bbbb cccc
            hexout = ' '.join(hexout[l:l + 4] for l in range(0, len(hexout), 4))

            # print('{}  {:<39} |{:<16}|'.format(address, hexout, asciiout))
            result.append([address, hexout, asciiout])

            # Decremento de 16 en modo que en las nuevas lineas se imprima el valor correcto
            byteslen -= 16

        return result

    def getSections(self):
        """
        Questa funzione serve trovare tutte le sezioni e i loro indirizzi dentro il programma specificato
        Per questa funzione ho fatto uso del modulo elftools.
        Ritorna: 1 dizionario con i nomi delle sezioni come chiave e gli indirizzi come valore
        (Questo per facilitare l utilizzo della funzione per cercare gli indirizzi avendo il nome)
        """
        sections = {}

        with open(self.file, 'rb') as f:
            elf = ELFFile(f)

            for section in elf.iter_sections():
                sections[section.name] = section['sh_addr']

        return sections

    def disAssembler(self, lines=25, ref_address=""):
        """
        Questa funzione serve per ricavare il codice in Assembler del programma dato
        Per questa funzione ho usato il modulo Capstone.
        Come parametri puo ricevere il numero di linee da ritornare e l'indirizzo da cui partire.
        Ritorna: 1 lista (indirizzo memoria, operazione, valori)
        """
        hx = unhexlify(''.join(self.hexdump()[1]))

        # creo un nuovo oggetto specificando l'architettura e il modo per assembler
        deco = Cs(CS_ARCH_X86, CS_MODE_64)
        counter_lines = 0

        result = []

        disassembler = deco.disasm(bytearray(hx), self.getSections()[".text"] if len(ref_address) == 0 else int(ref_address))

        for _ in disassembler:
            if lines == -1:
                result.append([_.address, _.mnemonic, _.op_str])
            else:
                result.append([_.address, _.mnemonic, _.op_str]) if counter_lines < lines else None
                counter_lines += 1

            # print("0x{:08X} {} {}".format(_.address, _.mnemonic, _.op_str))

        return result

    def getStrings(self):
        """
        Questa funzione serve per ricavare tutte le stringhe in chiaro dentro il programma dato
        Per questa funzione ho usato il module re per usare dei pattern di ricerca
        Ritorna: 1 lista con tutte le stringhe trovate
        """
        strings = []

        # Per non avere problemi nella codifica ho dovuto cambiare l'encoding
        for r in open(self.file, 'r', encoding='ISO-8859-1'):
            # Cerco valori ascci tra 32 (espazio) e 126 (~)
            string = re.findall("[\x1f-\x7e]{4,}", r)
            if len(string) != 0:
                for s in string: strings.append(s)

        return strings

    def searchString(self, string):
        """
        Questa funzione serve per cercare delle stringhe
        Come parametro riceve il nome della stringa da cercare
        Ritorna: 1 lista con tutti i match
        """
        result = []
        for s in self.getStrings():
            if string.lower() in s.lower(): result.append(s)

        return result
