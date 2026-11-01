import pyautogui
import time

print("Posicione o mouse onde deseja clicar...")
time.sleep(3)
print(pyautogui.position()) # Isso vai te dar algo como Point(x=1200, y=300)
