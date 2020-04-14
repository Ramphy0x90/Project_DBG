import platform
import sys, os
import disassembler
from npyscreen import *
from signal import signal, SIGINT
from CustomColor import CustomColor as toColor


class Terminal:
    """
    Questa classe serve per interfacciare tutte le funzioni create nella classe Disassembler con l'utente
    da terminale.
    """
    OS = platform.system().lower()

    def __init__(self, tui, disasm):

        self.tui = tui
        self.Disassemble = disasm
        self.current_address = '0x{:08X}'.format(self.Disassemble.getSections()[".text"])

        # Per tutti i comandi usabili dalla termimnale ho creato una matrice contente un dizionario e un'altra
        # lista. Nel dizionario uso come chiave 2 parole separate dal punto e virgola, con la funzione rispettiva
        # come valore
        self.commands = [
            [{"clear;cc": self.clear}, "Clear the terminal"],
            [{"graphic;v": self.graphic}, "Get the graphic mode of the program"],
            [{"disasm;da": self.disasm}, "Assembler code of debugged program"],
            [{"hexdump;hx": self.hexdump}, "Hex code of debugged code"],
            [{"sections;se": self.sections}, "Get sections names"],
            [{"strings;st": self.strings}, "Get strings of debugged program"],
            [{"search;ss": self.searchString}, "Search strings on debugged program"],
            [{"address;sa": self.setAddress}, "Set poin   ter to memory address"],
            [{"banner;banner": self.banner}, "Get the banner"],
            [{"help;h": self.bannerHelp}, "This banner"],
            [{"^C;."}, "Exit from visual mode"],
            [{"exit;exit": sys.exit}, "Exit"]
        ]

        self.banner = """

          _____                                 _ _           
         / ____|                               | | |          
        | |     _ __ ___  _ __   ___  ___    __| | |__   __ _ 
        | |    | '__/ _ \| '_ \ / _ \/ __|  / _` | '_ \ / _` |
        | |____| | | (_) | | | | (_) \__ \ | (_| | |_) | (_| |
         \_____|_|  \___/|_| |_|\___/|___/  \__,_|_.__/ \__, |
                                                         __/ |
                                                        |___/ 
           {}
           {}
               """.format(toColor("by Ramphy Aquino Nova", "YELLOW"), toColor("I2a", "DBLUE"))

    def bannerHelp(self):
        description = "School project of module M122 by Ramphy Aquino Nova I2a.\n\n" \
                      "Commands: \n"

        print(description)

        for i in self.commands:
            for c in i[0]:
                comL, comS = c.split(";")
                print('{:<10}  {:<6} |{:<16}'.format(comL, comS, i[1]))

    def clear(self):
        os.system("clear" if self.OS != "windows" else "cls")

    def graphic(self):
        self.tui.run()
        self.tui.switchForm("MAIN")

    def disasm(self, lines=25):
        # In questa funzione come in altre nel resto del programma ho usato una classe fatta da me per
        # colorare le stringhe
        for _ in self.Disassemble.disAssembler(lines=lines, ref_address=str(int(self.current_address, 0))):
            address = toColor("0x{:08X}".format(_[0]), "GREEN")
            operation = toColor(_[1], "YELLOW")
            values = toColor(" ".join(_[2].split(" ")[0:2] + [""]), "DBLUE") + \
                     toColor(" ".join(_[2].split(" ")[2:]), "PURPLE")

            print("{} {} {}".format(address, operation, values))

    def hexdump(self, byteslen='304'):
        for _ in self.Disassemble.getHexdump(byteslen=byteslen, ref_address=self.current_address):
            address = toColor(_[0], "GREEN")
            hexvalues = _[1]
            asciivalues = toColor("|{:<16}|".format(_[2]), "YELLOW")

            print('{}  {:<39} {}'.format(address, hexvalues, asciivalues))

    def sections(self):
        for _ in self.Disassemble.getSections():
            print(toColor('0x{:08X}'.format(self.Disassemble.getSections()[_]), "GREEN"), toColor(_, "YELLOW"))

    def strings(self):
        for _ in self.Disassemble.getStrings():
            print(_)

    def searchString(self, string):
        result = self.Disassemble.searchString(string)

        for _ in result:
            print(_)

        if not len(result):
            print(toColor("[!] Any result", "YELLOW"))

    def setAddress(self, address):
        # Questa funzione serve per impostare l'indirizzo dal quale si partira per ricavare i dati
        max_address = self.Disassemble.getHexdump()[-1][0]
        if int(address, 0) <= int(max_address, 0):
            self.current_address = '0x{:08X}'.format(int(address, 0))
        else:
            print(toColor("[*] Empty address", "RED"))
            print(toColor("[!] Max address: ", "YELLOW") + toColor(max_address, "GREEN"))

    def banner(self):
        print(self.banner)

    def run(self):
        print(self.banner)

        while True:
            address = toColor("{}".format(self.current_address), "YELLOW")

            command = input("\n[{}]>>> ".format(address)).lower()
            cExists = False

            for _ in self.commands:
                for key in _[0]:
                    index = self.commands.index(_)
                    param = command.split(" ")

                    if param[0] in key.split(";"):
                        # Tutte le funzioni della terminale possono essere usate senza parametri tranne le seguenti
                        # dove si devono specificare alcuni parametri
                        if len(param) > 1:
                            if key.split(";")[0] == "disasm" and len(param) > 1:
                                self.commands[index][0][key](lines=int(param[1]))
                            elif key.split(";")[0] == "hexdump" and len(param) > 1:
                                self.commands[index][0][key](byteslen=param[1])
                            elif key.split(";")[0] == "search" and len(param) > 1:
                                self.commands[index][0][key](param[1])
                            elif key.split(";")[0] == "address" and len(param) > 1:
                                self.commands[index][0][key](param[1])
                        else:
                            if command in key.split(";"):
                                self.commands[index][0][key]()

                        cExists = True
                        break
                    elif len(command) == 0:
                        cExists = True

            if not cExists:
                print(toColor("[!] Command not found", "RED"))


class MainTui(FormBaseNew):
    """
    Questa classe serve per creare gli oggetti che faranno parte di tutta la GUI della classe Disassembler.
    Per fare tutta la GUI è stato usato il modulo Npyscreen
    """
    frames = {}

    padding = 1
    window_height, window_width = 0, 0

    def create(self):
        self.window_height, self.window_width = self.useable_space()

        section_width = (self.window_width // 2) - self.padding * 2
        section_height = self.window_height - self.padding * 4

        self.frames['e_section'] = self.add(BoxTitle, name="Extended section", max_width=section_width,
                                            max_height=section_height,
                                            rely=self.padding * 2,
                                            contained_widget_arguments={
                                                'color': 'GOOD',
                                                'widgets_inherit_color': True}
                                            )

        self.frames['s_section0'] = self.add(BoxTitle, name="Small section 0", max_width=section_width,
                                             max_height=(section_height // 2) + 1,
                                             relx=(self.window_width - section_width) - self.padding * 2,
                                             rely=self.padding * 2,
                                             contained_widget_arguments={
                                                 'color': 'NO_EDIT',
                                                 'widgets_inherit_color': True}
                                             )

        self.frames['s_section1'] = self.add(BoxTitle, name="Small section 1", max_width=section_width,
                                             max_height=(section_height // 2),
                                             relx=(self.window_width - section_width) - self.padding * 2,
                                             contained_widget_arguments={
                                                 'color': 'STANDOUT',
                                                 'widgets_inherit_color': True}
                                             )

    def addContent(self, section, value):
        self.frames[section].values.append(value)

    def setContent(self, section, values):
        self.frames[section].values = values

    def deleteContent(self, section):
        self.frames[section].values.clear()


class Main(StandardApp):
    """
    Questa classe serve per inizializzare tutta la schermata della GUI e per riempire i widget
    """

    def __init__(self, disasm):
        super().__init__()
        self.Disassemble = disasm

    def onStart(self):
        self.addForm("MAIN", MainTui, name="Disassembler")

        self.maintui = self.getForm("MAIN")

        for _ in self.Disassemble.disAssembler(lines=-1, ref_address="0"):
            address = '0x{:08X}'.format(_[0])
            operation = _[1]
            operands = _[2]

            self.maintui.addContent("e_section", "{} {} {}".format(address, operation, operands))

        for _ in self.Disassemble.getSections():
            address = '0x{:08X}'.format(self.Disassemble.getSections()[_])
            self.maintui.addContent("s_section0", address + " " + _)

        for _ in self.Disassemble.getStrings():
            self.maintui.addContent("s_section1", _)


Disassemble = disassembler.Disassembler(sys.argv[1])
TUI = Main(Disassemble)
Terminal = Terminal(TUI, Disassemble)


def handler(signal_received, frame):
    TUI.switchForm(None)


if __name__ == '__main__':
    # Ho usato il modulo signal per fare un handler per quando l'utente schiaccia ^C
    # Questo serve per uscire dalla versione grafica ma senza uscire interamente da tutto il programma
    signal(SIGINT, handler)

    try:
        Terminal.run()
    except AttributeError:
        pass
