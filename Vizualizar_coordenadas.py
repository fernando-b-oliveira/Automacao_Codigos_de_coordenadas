import tkinter as tk
from pynput import mouse, keyboard
import threading
import time

# Variáveis globais para guardar a posição e as ações
current_x = 0
current_y = 0
last_action = "Nenhuma"
action_time = 0
keys_held = set() # Guarda quais teclas estão pressionadas no momento

# ================= EVENTOS DO MOUSE =================
def on_move(x, y):
    global current_x, current_y
    current_x = x
    current_y = y

def on_click(x, y, button, pressed):
    global current_x, current_y, last_action, action_time
    current_x = x
    current_y = y
    
    if pressed:
        btn_name = str(button).replace('Button.', '')
        if btn_name == 'left': btn_name = 'ESQUERDO'
        elif btn_name == 'right': btn_name = 'DIREITO'
        elif btn_name == 'middle': btn_name = 'MEIO'
        
        last_action = f"CLIQUE {btn_name}"
        action_time = time.time()

# ================= EVENTOS DO TECLADO =================
def get_key_name(key):
    # Traduz e limpa os nomes das teclas para ficarem bonitos na tela
    if hasattr(key, 'name') and key.name is not None:
        name = key.name.replace('_l', '').replace('_r', '').replace('_gr', '')
        mapping = {
            'ctrl': 'Ctrl', 'shift': 'Shift', 'alt': 'Alt', 'cmd': 'Win',
            'enter': 'Enter', 'space': 'Espaço', 'esc': 'Esc',
            'backspace': 'Backspace', 'tab': 'Tab', 'delete': 'Del'
        }
        if name.startswith('f') and name[1:].isdigit():
            return name.upper() # F1, F2, F3...
        return mapping.get(name, name.capitalize())
    else:
        try:
            # Tratamento especial para quando usamos Ctrl + Letra
            if hasattr(key, 'char') and key.char is not None:
                if ord(key.char) < 32: 
                    return chr(ord(key.char) + 64).upper()
                return key.char.upper()
        except:
            pass
        return str(key).replace("'", "").upper()

def on_press(key):
    global last_action, action_time
    key_name = get_key_name(key)
    
    if key_name not in keys_held:
        keys_held.add(key_name)
        
    # Organiza para que o Ctrl/Shift/Alt apareçam primeiro na string
    modifiers = [k for k in ['Ctrl', 'Shift', 'Alt', 'Win'] if k in keys_held]
    others = [k for k in keys_held if k not in ['Ctrl', 'Shift', 'Alt', 'Win']]
    
    last_action = " + ".join(modifiers + others)
    action_time = time.time()

def on_release(key):
    key_name = get_key_name(key)
    if key_name in keys_held:
        keys_held.remove(key_name)

# ================= MONITORES =================
def start_listeners():
    # Inicia o mouse e o teclado ao mesmo tempo
    m_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    k_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    
    m_listener.start()
    k_listener.start()
    
    m_listener.join()
    k_listener.join()

def update_label():
    global last_action, action_time
    
    # Apaga o texto da ação após 2 segundos
    if time.time() - action_time > 2:
        last_action = "Nenhuma"
        keys_held.clear() # Limpa as teclas travadas por precaução
        
    texto = f"X: {int(current_x)} | Y: {int(current_y)}\nAção: {last_action}"
    label_var.set(texto)
    
    root.after(50, update_label)

def fechar_app(event):
    root.destroy()

# ================= INTERFACE (TKINTER) =================
root = tk.Tk()
root.title("Legenda do Mouse e Teclado")

root.attributes("-topmost", True)
root.overrideredirect(True)
root.attributes("-alpha", 0.85)

# Aumentei a largura de 250 para 320 para caber atalhos como "Ctrl + Shift + Esc"
window_width = 320
window_height = 80
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = screen_width - window_width - 30
y_pos = screen_height - window_height - 60

root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
root.configure(bg='black')

label_var = tk.StringVar()
label_var.set("Iniciando...")

label = tk.Label(root, textvariable=label_var, font=("Consolas", 14, "bold"), 
                 fg="lime", bg="black", justify="center")
label.pack(expand=True, fill="both")

root.bind("<Escape>", fechar_app)

# Inicia as threads em segundo plano
listener_thread = threading.Thread(target=start_listeners, daemon=True)
listener_thread.start()

update_label()
root.mainloop()
