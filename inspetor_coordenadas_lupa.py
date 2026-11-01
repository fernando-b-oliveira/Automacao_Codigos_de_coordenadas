import sys
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from pynput import mouse, keyboard
from docx import Document

# Configurações de tamanho (em pixels)
CHUNK_SIZE = 256
MICRO_SIZE = 16

# Lista global para armazenar as ações que irão para o Word
action_log = []

class OverlayGrade(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.mouse_pos = QtCore.QPoint(0, 0)
        self.initUI()
        
        # Pré-renderiza a grade em uma imagem estática para não consumir CPU
        self.grid_pixmap = QtGui.QPixmap(self.size())
        self.grid_pixmap.fill(QtCore.Qt.transparent)
        self.render_grid()

        # Timer de 60fps (16ms) para atualizar apenas a posição visual do mouse
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_mouse)
        self.timer.start(16)

    def initUI(self):
        # Remove as bordas, força a ficar sempre no topo e, mais importante:
        # WindowTransparentForInput torna a janela "invisível" para o mouse (clique vazado)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | 
                            QtCore.Qt.WindowStaysOnTopHint | 
                            QtCore.Qt.Tool | 
                            QtCore.Qt.WindowTransparentForInput)
        
        # Fundo transparente
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Cobre a tela inteira
        screen_geometry = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry(screen_geometry)
        
    def render_grid(self):
        painter = QtGui.QPainter(self.grid_pixmap)
        
        # Estilos das linhas (Cor RGB, Transparência, Espessura)
        pen_micro = QtGui.QPen(QtGui.QColor(0, 255, 0, 30), 1)   # Verde bem claro para micros
        pen_chunk = QtGui.QPen(QtGui.QColor(0, 255, 0, 120), 2)  # Verde mais forte para chunks
        
        w = self.width()
        h = self.height()

        # Desenha a grade de Micro-quadrados
        painter.setPen(pen_micro)
        for x in range(0, w, MICRO_SIZE):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, MICRO_SIZE):
            painter.drawLine(0, y, w, y)

        # Desenha a grade de Chunks
        painter.setPen(pen_chunk)
        for x in range(0, w, CHUNK_SIZE):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, CHUNK_SIZE):
            painter.drawLine(0, y, w, y)
            
        painter.end()

    def update_mouse(self):
        # Pega a posição global do mouse do Windows/OS
        pos = QtGui.QCursor.pos()
        if self.mouse_pos != pos:
            self.mouse_pos = pos
            self.update() # Força a tela a se redesenhar (chama o paintEvent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        
        # Desenha a grade pré-renderizada (muito mais leve para o computador)
        painter.drawPixmap(0, 0, self.grid_pixmap)

        # Calcula em qual micro-quadrado o mouse está para encaixar o destaque
        x_snap = (self.mouse_pos.x() // MICRO_SIZE) * MICRO_SIZE
        y_snap = (self.mouse_pos.y() // MICRO_SIZE) * MICRO_SIZE

        # Desenha o quadrado vermelho translúcido destacando a posição exata
        highlight_color = QtGui.QColor(255, 0, 0, 150)
        painter.fillRect(x_snap, y_snap, MICRO_SIZE, MICRO_SIZE, highlight_color)

# === Funções de Rastreamento (Logging) ===

def on_click(x, y, button, pressed):
    if pressed:
        timestamp = datetime.now().strftime("%H:%M:%S")
        chunk_x, chunk_y = int(x // CHUNK_SIZE), int(y // CHUNK_SIZE)
        micro_x, micro_y = int(x // MICRO_SIZE), int(y // MICRO_SIZE)
        
        log = (f"[{timestamp}] CLIQUE: Botão {button.name} | "
               f"Posição Tela: ({int(x)}, {int(y)}) | "
               f"Chunk: [{chunk_x}, {chunk_y}] | Micro: [{micro_x}, {micro_y}]")
        action_log.append(log)

def on_press(key):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        log = f"[{timestamp}] TECLADO: Digitou '{key.char}'"
        action_log.append(log)
    except AttributeError:
        log = f"[{timestamp}] TECLADO: Pressionou {key.name.upper()}"
        action_log.append(log)

    # Condição de parada: Se apertar ESC, encerra a aplicação
    if key == keyboard.Key.esc:
        QtWidgets.QApplication.quit()
        return False # Interrompe o listener de teclado

def gerar_relatorio_word():
    print("Gerando relatório no Word...")
    doc = Document()
    doc.add_heading('Relatório de Ações - Mapeamento de Tela', 0)
    
    doc.add_paragraph(f"Gravação iniciada/encerrada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    doc.add_paragraph(f"Configurações: Chunks de {CHUNK_SIZE}x{CHUNK_SIZE}px | Micros de {MICRO_SIZE}x{MICRO_SIZE}px\n")
    
    for acao in action_log:
        doc.add_paragraph(acao)
        
    nome_arquivo = f"relatorio_atividades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.save(nome_arquivo)
    print(f"Relatório salvo com sucesso: {nome_arquivo}")

# === Inicialização do Programa ===

def main():
    # Previne que resoluções altas (4K) desalinhem a grade no Windows
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    
    # Inicia os ouvintes em segundo plano (não interferem no trabalho)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)
    
    mouse_listener.start()
    keyboard_listener.start()
    
    # Inicia a sobreposição visual
    overlay = OverlayGrade()
    overlay.show()
    
    print("Gravação iniciada! Pressione a tecla 'ESC' a qualquer momento para parar e salvar o Word.")
    
    # Loop principal da interface gráfica
    app.exec_()
    
    # Quando o app.exec_() for encerrado (pela tecla ESC), o código continua aqui:
    mouse_listener.stop()
    gerar_relatorio_word()
    sys.exit()

if __name__ == '__main__':
    main()
