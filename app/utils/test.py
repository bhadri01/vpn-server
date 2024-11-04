import pyfiglet
from termcolor import colored
import itertools

def rainbow_text(text):
    colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']
    color_cycle = itertools.cycle(colors)
    return ''.join(colored(char, next(color_cycle)) for char in text)

# List of example fonts
fonts = pyfiglet.FigletFont.getFonts()

# Generate and print each font style with rainbow effect
for font in fonts:
    ascii_banner = pyfiglet.figlet_format("VPN", font=font)
    print(f"\nFont: {font}\n")
    print(rainbow_text(ascii_banner))