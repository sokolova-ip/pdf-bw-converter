"""
Основной модуль для запуска приложения
"""

import tkinter as tk
from gui import PDFConverterGUI

def main():
    """Основная функция запуска приложения"""
    root = tk.Tk()
    app = PDFConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()