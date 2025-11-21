"""
Модуль для конвертации PDF в черно-белый формат
"""

import os
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance
import io
import tempfile
import shutil

class PDFToBWConverter:
    """Класс для конвертации PDF в черно-белый формат"""
    
    def __init__(self):
        self.output_size = "original"
        self.brightness = 1.0
        self.contrast = 1.0
        self.sharpness = 1.0
        self.quality = 75
        self.preserve_orientation = True

    def set_output_size(self, size="original", preserve_orientation=True):
        """Установка размера выходной страницы"""
        valid_sizes = {
            "original": "original",
            "A4": (595, 842),
            "A3": (842, 1191),
            "A5": (420, 595),
            "Letter": (612, 792),
            "Legal": (612, 1008)
        }
        
        if size in valid_sizes:
            self.output_size = size
            self.preserve_orientation = preserve_orientation
            return True
        elif isinstance(size, tuple) and len(size) == 2:
            self.output_size = size
            self.preserve_orientation = preserve_orientation
            return True
        else:
            return False

    def set_image_settings(self, brightness=1.0, contrast=1.0, sharpness=1.0, quality=75):
        """Настройка параметров изображения"""
        self.brightness = max(0.1, min(3.0, brightness))
        self.contrast = max(0.1, min(3.0, contrast))
        self.sharpness = max(0.1, min(3.0, sharpness))
        self.quality = max(10, min(100, quality))

    def is_already_grayscale(self, image, threshold=0.95):
        """
        Проверяет, является ли изображение уже черно-белым
        
        Args:
            image: PIL Image объект
            threshold: порог для определения черно-белого
        
        Returns:
            bool: True если изображение уже черно-белое
        """
        if image.mode == 'L':
            return True
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        pixels = list(image.getdata())
        sample_pixels = pixels[::10]
        
        grayscale_count = 0
        total_sample = len(sample_pixels)
        
        for r, g, b in sample_pixels:
            if r == g == b:
                grayscale_count += 1
        
        grayscale_ratio = grayscale_count / total_sample
        return grayscale_ratio >= threshold

    def check_pdf_is_grayscale(self, pdf_path, sample_pages=3, threshold=0.95):
        """
        Проверяет, является ли PDF уже черно-белым
        
        Args:
            pdf_path: путь к PDF файлу
            sample_pages: количество страниц для проверки
            threshold: порог для определения черно-белого
        
        Returns:
            tuple: (is_grayscale, grayscale_pages, total_checked)
        """
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            if sample_pages == 0 or sample_pages >= total_pages:
                pages_to_check = range(total_pages)
            else:
                pages_to_check = [0]
                if total_pages > 1:
                    pages_to_check.append(total_pages - 1)
                if total_pages > 2:
                    middle = total_pages // 2
                    pages_to_check.append(middle)
                if total_pages > 3 and sample_pages > 3:
                    pages_to_check.extend(range(1, min(sample_pages - 2, total_pages - 2)))
            
            grayscale_pages = 0
            checked_pages = 0
            
            for page_num in pages_to_check:
                if page_num >= total_pages:
                    continue
                    
                page = doc[page_num]
                mat = fitz.Matrix(0.5, 0.5)
                pix = page.get_pixmap(matrix=mat)
                
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                
                if self.is_already_grayscale(img, threshold):
                    grayscale_pages += 1
                
                checked_pages += 1
            
            doc.close()
            
            is_grayscale = (grayscale_pages == checked_pages)
            return is_grayscale, grayscale_pages, checked_pages
            
        except Exception as e:
            print(f"Ошибка при проверке PDF: {e}")
            return False, 0, 0

    def apply_image_enhancements(self, image):
        """Применение улучшений к изображению"""
        if image.mode != 'L':
            image = image.convert('L')
        
        if self.brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(self.brightness)
        
        if self.contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.contrast)
        
        if self.sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpness)
        
        return image

    def get_page_dimensions(self, page):
        """Получение размеров страницы с учетом настроек"""
        original_rect = page.rect
        original_width = original_rect.width
        original_height = original_rect.height
        
        if self.output_size == "original":
            return (original_width, original_height)
        
        size_map = {
            "A4": (595, 842),
            "A3": (842, 1191),
            "A5": (420, 595),
            "Letter": (612, 792),
            "Legal": (612, 1008)
        }
        
        if isinstance(self.output_size, str) and self.output_size in size_map:
            base_size = size_map[self.output_size]
        elif isinstance(self.output_size, tuple):
            base_size = self.output_size
        else:
            base_size = (original_width, original_height)
        
        if self.preserve_orientation:
            is_landscape = original_width > original_height
            base_width, base_height = base_size
            
            target_is_landscape = base_width > base_height
            if is_landscape != target_is_landscape:
                base_size = (base_height, base_width)
        
        return base_size

    def convert_pdf_to_bw(self, input_pdf_path, output_pdf_path, progress_callback=None):
        """
        Конвертация PDF в черно-белый с сохранением оригинального разрешения
        
        Args:
            input_pdf_path (str): Путь к входному PDF файлу
            output_pdf_path (str): Путь для сохранения выходного PDF файла
            progress_callback (callable): Функция для отслеживания прогресса
        
        Returns:
            bool: True если конвертация успешна
        """
        try:
            if progress_callback:
                progress_callback(0, "Проверка формата PDF...")
            
            is_grayscale, grayscale_pages, checked_pages = self.check_pdf_is_grayscale(
                input_pdf_path, sample_pages=3, threshold=0.9
            )
            
            if is_grayscale:
                if progress_callback:
                    progress_callback(100, "PDF уже черно-белый - копирование без изменений")
                
                shutil.copy2(input_pdf_path, output_pdf_path)
                return True
            
            input_doc = fitz.open(input_pdf_path)
            output_doc = fitz.open()
            
            total_pages = len(input_doc)
            
            for page_num in range(total_pages):
                if progress_callback:
                    progress = (page_num / total_pages) * 100
                    progress_callback(progress, f"Обработка страницы {page_num + 1}/{total_pages}")
                
                page = input_doc[page_num]
                output_width, output_height = self.get_page_dimensions(page)
                
                original_rect = page.rect
                original_width = original_rect.width
                original_height = original_rect.height
                
                scale_x = output_width / original_width
                scale_y = output_height / original_height
                
                mat = fitz.Matrix(2.0 * scale_x, 2.0 * scale_y)
                pix = page.get_pixmap(matrix=mat)
                
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                
                bw_img = self.apply_image_enhancements(img)
                
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_path = temp_file.name
                    bw_img.save(temp_path, 'JPEG', quality=self.quality, optimize=True)
                
                new_page = output_doc.new_page(width=output_width, height=output_height)
                rect = fitz.Rect(0, 0, output_width, output_height)
                new_page.insert_image(rect, filename=temp_path)
                
                os.unlink(temp_path)
            
            output_doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
            output_doc.close()
            input_doc.close()
            
            if progress_callback:
                progress_callback(100, "Конвертация завершена!")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Ошибка: {e}")
            return False

    def get_preview_image(self, pdf_path, page_num=0, preview_size=(300, 400)):
        """Получает изображение для предпросмотра"""
        try:
            doc = fitz.open(pdf_path)
            if page_num >= len(doc):
                page_num = 0
            
            page = doc[page_num]
            
            # Вычисляем масштаб для предпросмотра
            original_width = page.rect.width
            original_height = page.rect.height
            
            scale_x = preview_size[0] / original_width
            scale_y = preview_size[1] / original_height
            scale = min(scale_x, scale_y) * 0.9  # Немного меньше для отступов
            
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat)
            
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            doc.close()
            return img
            
        except Exception as e:
            print(f"Ошибка при получении предпросмотра: {e}")
            return None

    def apply_preview_enhancements(self, image, brightness, contrast, sharpness):
        """Применяет настройки к изображению для предпросмотра"""
        if image.mode != 'L':
            image = image.convert('L')
        
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(sharpness)
        
        return image