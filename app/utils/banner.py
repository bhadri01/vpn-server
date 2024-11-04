import pyfiglet
from termcolor import colored
import itertools

def rainbow_text(text):
    # Define rainbow colors to cycle through
    colors = ["white"]
    color_cycle = itertools.cycle(colors)
    
    # Apply the colors to each character in the text
    rainbow_text = ''.join(colored(char, next(color_cycle)) for char in text)
    return rainbow_text

# Generate ASCII text using pyfiglet
ascii_banner = pyfiglet.figlet_format("VPN SERVER",font="ansi_regular")
