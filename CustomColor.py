class CustomColor:
    colors = {
        "BLACK": "\33[90m",
        "RED": "\33[91m",
        "GREEN": "\33[92m",
        "YELLOW": "\33[33m",
        "BLUE": "\33[94m",
        "DBLUE": "\u001b[34;1m",
        "PURPLE": "\33[95m",
        "DEFAULT": "\u001b[0m"
    }

    def __init__(self, string, color):
        self.string = string
        self.color = color

    # Uso la funzione String del oggetto per fare il return del risultato finale
    def __str__(self):
        return self.colors[self.color] + self.string + self.colors['DEFAULT']

    # Mi sono creato la funzione __add__ per poter concatenare istanze di Customcolor
    def __add__(self, s):
        return self.__str__() + str(s)