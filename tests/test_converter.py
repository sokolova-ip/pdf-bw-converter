"""
Тесты для модуля конвертера PDF
"""

import unittest
import os
import tempfile
from src.converter import PDFToBWConverter

class TestPDFToBWConverter(unittest.TestCase):
    """Тесты для класса PDFToBWConverter"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.converter = PDFToBWConverter()
    
    def test_set_output_size(self):
        """Тест установки размера выходного файла"""
        # Тест стандартных размеров
        self.assertTrue(self.converter.set_output_size("A4"))
        self.assertEqual(self.converter.output_size, "A4")
        
        # Тест пользовательского размера
        self.assertTrue(self.converter.set_output_size((800, 600)))
        self.assertEqual(self.converter.output_size, (800, 600))
        
        # Тест неверного размера
        self.assertFalse(self.converter.set_output_size("Invalid"))
    
    def test_set_image_settings(self):
        """Тест установки настроек изображения"""
        self.converter.set_image_settings(
            brightness=1.5,
            contrast=1.2,
            sharpness=0.8,
            quality=90
        )
        
        self.assertEqual(self.converter.brightness, 1.5)
        self.assertEqual(self.converter.contrast, 1.2)
        self.assertEqual(self.converter.sharpness, 0.8)
        self.assertEqual(self.converter.quality, 90)
        
        # Тест граничных значений
        self.converter.set_image_settings(brightness=5.0)  # Должно быть ограничено до 3.0
        self.assertEqual(self.converter.brightness, 3.0)
        
        self.converter.set_image_settings(brightness=-1.0)  # Должно быть ограничено до 0.1
        self.assertEqual(self.converter.brightness, 0.1)

if __name__ == "__main__":
    unittest.main()