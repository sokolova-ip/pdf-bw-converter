#!/usr/bin/env python3
"""
Точка входа для запуска конвертера PDF в черно-белый
"""

import sys
import os

# Добавляем src в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main()