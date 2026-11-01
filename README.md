# RPA DevTools & Step Activity Tracker
> Suíte de ferramentas em Python para desenvolvedores de automação desktop (RPA): gravador de passos com documentação em Word e lupa de precisão de coordenadas em PyQt5.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green.svg)
![Automation](https://img.shields.io/badge/RPA-Pynput%20%7C%20PyAutoGUI-brightgreen.svg)

---

## 📌 Ferramentas Inclusas

### 1. `copiador_de_passos.py` (Activity Step Documenter)
Grava as ações de teclado e mouse do usuário em tempo real durante a execução de um processo manual e gera automaticamente um documento estruturado no Microsoft Word (`.docx`), facilitando a criação de documentações de processo (PDDs) e especificações técnicas de automação.

### 2. `inspetor_coordenadas_lupa.py` / `hacker_de_cordenadas.py` (Pixel Magnifier & Coordinate HUD)
Interface flutuante em **PyQt5** com zoom em grade de pixels que acompanha o cursor do mouse, exibindo as coordenadas exatas $(X, Y)$ na tela para mapeamento de botões e campos em aplicações legadas.

### 3. `Vizualizar_coordenadas.py` & `Mapear_por_click.py`
Utilitários leves de linha de comando e interface Tkinter para verificação rápida de cliques e posições de tela.

## 🛠️ Como Utilizar

```bash
pip install pyqt5 pynput python-docx pyautogui
python inspetor_coordenadas_lupa.py
```
