import tkinter as tk
from pynput import mouse, keyboard
from docx import Document
import time
import os
import re  # <- Biblioteca nova para limpar o texto

class RastreadorAtividades:
    def __init__(self, root):
        self.root = root
        self.root.title("Gravador de Ações")
        
        # Mantém a janela sempre no topo, independente da aba
        self.root.attributes('-topmost', True)
        self.root.geometry("350x200")
        
        # Variáveis de controle
        self.gravando = True
        self.pausado = False
        self.historico = []
        self.ultimo_tempo = time.time()
        
        # Interface Gráfica (Caixa de texto e Botões)
        self.texto_status = tk.Text(root, height=8, width=40, state='disabled')
        self.texto_status.pack(pady=5)
        
        frame_botoes = tk.Frame(root)
        frame_botoes.pack(pady=5)
        
        self.btn_pausar = tk.Button(frame_botoes, text="Pausar", command=self.alternar_pausa, width=10)
        self.btn_pausar.grid(row=0, column=0, padx=5)
        
        self.btn_parar = tk.Button(frame_botoes, text="Parar e Salvar", command=self.parar_e_salvar, width=12)
        self.btn_parar.grid(row=0, column=1, padx=5)

        self.atualizar_caixa_texto("Gravação iniciada...")

        # Iniciando as Threads de escuta do Mouse e Teclado
        self.listener_teclado = keyboard.Listener(on_press=self.ao_pressionar_tecla)
        self.listener_mouse = mouse.Listener(
            on_click=self.ao_clicar_mouse,
            on_scroll=self.ao_rolar_mouse
        )
        
        self.listener_teclado.start()
        self.listener_mouse.start()

    def registrar_acao(self, acao):
        """Registra a ação se não estiver pausado e calcula o tempo desde a última ação."""
        if self.gravando and not self.pausado:
            tempo_atual = time.time()
            tempo_decorrido = tempo_atual - self.ultimo_tempo
            self.ultimo_tempo = tempo_atual
            
            # Formata o log
            registro = f"[+{tempo_decorrido:.2f}s] {acao}"
            self.historico.append(registro)
            
            # Atualiza a caixinha flutuante com a última ação
            self.atualizar_caixa_texto(registro)

    def ao_pressionar_tecla(self, key):
        try:
            # Teclas normais (letras, números)
            self.registrar_acao(f"Digitou a tecla '{key.char}'")
        except AttributeError:
            # Teclas especiais (Ctrl, Shift, Enter, etc)
            self.registrar_acao(f"Apertou a tecla especial '{key}'")

    def ao_clicar_mouse(self, x, y, button, pressed):
        if pressed: 
            nome_botao = "Botão Esquerdo" if button == mouse.Button.left else "Botão Direito" if button == mouse.Button.right else "Botão do Meio"
            self.registrar_acao(f"Clicou ({nome_botao}) na coordenada X:{x} Y:{y}")

    def ao_rolar_mouse(self, x, y, dx, dy):
        direcao = "para cima" if dy > 0 else "para baixo"
        self.registrar_acao(f"Rolou o scroll ({direcao}) na coordenada X:{x} Y:{y}")

    def alternar_pausa(self):
        self.pausado = not self.pausado
        if self.pausado:
            self.btn_pausar.config(text="Retomar")
            self.atualizar_caixa_texto("--- GRAVAÇÃO PAUSADA ---")
            self.ultimo_tempo = time.time() 
        else:
            self.btn_pausar.config(text="Pausar")
            self.ultimo_tempo = time.time()
            self.atualizar_caixa_texto("--- GRAVAÇÃO RETOMADA ---")

    def atualizar_caixa_texto(self, texto):
        self.texto_status.config(state='normal')
        self.texto_status.insert(tk.END, texto + "\n")
        self.texto_status.see(tk.END) 
        self.texto_status.config(state='disabled')

    def parar_e_salvar(self):
        self.gravando = False
        self.listener_teclado.stop()
        self.listener_mouse.stop()
        
        self.atualizar_caixa_texto("Salvando documento...")
        self.salvar_no_word()
        
        self.root.quit()

    def salvar_no_word(self):
        doc = Document()
        doc.add_heading('Histórico de Ações do Usuário', 0)
        
        for linha in self.historico:
            # FILTRO MÁGICO: Remove qualquer caractere de controle invisível que trave o Word
            linha_limpa = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', linha)
            doc.add_paragraph(linha_limpa)
            
        nome_arquivo = "historico_acoes.docx"
        doc.save(nome_arquivo)
        print(f"Arquivo '{nome_arquivo}' salvo com sucesso na pasta atual: {os.getcwd()}")

if __name__ == "__main__":
    janela_principal = tk.Tk()
    app = RastreadorAtividades(janela_principal)
    janela_principal.mainloop()
