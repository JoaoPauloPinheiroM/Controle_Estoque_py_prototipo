import importlib.util
import os
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import pandas
import sys

def carregar_modulo_na_pasta(modulo_name, arquivo):
    spec = importlib.util.spec_from_file_location(modulo_name, arquivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

# Determina o diretório base: se estiver empacotado, usa o diretório do executável;
# caso contrário, usa o diretório do próprio arquivo.
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

caminho_modulo = os.path.join(base_dir, "controle_estoque.py")

controle_estoque = carregar_modulo_na_pasta("controle_estoque", caminho_modulo)
controle_estoque.main()
