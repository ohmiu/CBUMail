import sys
import colorama

colorama.init(autoreset=True)

def gradient_text(text, start_color, end_color):
    gradient = []
    for i in range(len(text)):
        ratio = i / (len(text) - 1)
        r = int((1 - ratio) * start_color[0] + ratio * end_color[0])
        g = int((1 - ratio) * start_color[1] + ratio * end_color[1])
        b = int((1 - ratio) * start_color[2] + ratio * end_color[2])
        gradient.append(f"\033[38;2;{r};{g};{b}m{text[i]}\033[0m")
    return ''.join(gradient)

def show():
    start_color = (255, 0, 0) 
    end_color = (0, 0, 255)
    text = """ .o88b. d8888b. db    db .88b  d88.  .d8b.  d888888b db
d8P  Y8 88  `8D 88    88 88'YbdP`88 d8' `8b   `88'   88
8P      88oooY' 88    88 88  88  88 88ooo88    88    88
8b      88~~~b. 88    88 88  88  88 88~~~88    88    88
Y8b  d8 88   8D 88b  d88 88  88  88 88   88   .88.   88booo.
 `Y88P' Y8888P' ~Y8888P' YP  YP  YP YP   YP Y888888P Y88888P
 """

    gradient_text_output = gradient_text(text, start_color, end_color)
    print(gradient_text_output)
