"""
Модуль графического интерфейса для конвертера PDF
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from PIL import ImageTk
import fitz

from converter import PDFToBWConverter

class PDFConverterGUI:
    """Класс графического интерфейса конвертера PDF"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер PDF в черно-белый")
        self.root.geometry("800x700")
        self.converter = PDFToBWConverter()
        
        self.input_file = None
        self.preview_image = None
        self.current_page = 0
        self.total_pages = 0
        self.original_preview = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        ttk.Label(main_frame, text="Конвертер PDF в черно-белый", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Фрейм для выбора файла и предпросмотра
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        top_frame.columnconfigure(1, weight=1)
        
        # Выбор файла
        file_frame = ttk.Frame(top_frame)
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        ttk.Label(file_frame, text="Выберите PDF файл:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.file_label = ttk.Label(file_frame, text="Файл не выбран", foreground="gray", wraplength=200)
        self.file_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="Обзор", command=self.browse_file).grid(row=1, column=1, padx=(5, 0))
        
        # Управление предпросмотром
        preview_controls = ttk.Frame(file_frame)
        preview_controls.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(preview_controls, text="Страница:").grid(row=0, column=0, sticky=tk.W)
        
        self.page_var = tk.StringVar(value="1")
        self.page_spinbox = ttk.Spinbox(preview_controls, from_=1, to=1, width=5, 
                                       textvariable=self.page_var, command=self.update_preview)
        self.page_spinbox.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Button(preview_controls, text="Обновить", 
                  command=self.update_preview).grid(row=0, column=2)
        
        # Область предпросмотра
        preview_frame = ttk.LabelFrame(top_frame, text="Предпросмотр", padding="5")
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.preview_label = ttk.Label(preview_frame, text="Выберите PDF файл для предпросмотра", 
                                      background="white", anchor=tk.CENTER)
        self.preview_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Разделитель
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Настройки размера
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(settings_frame, text="Размер выходного файла:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.size_var = tk.StringVar(value="original")
        size_combo = ttk.Combobox(settings_frame, textvariable=self.size_var, 
                                 values=["original", "A4", "A3", "A5", "Letter", "Legal"])
        size_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        self.orientation_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Сохранять ориентацию страниц", 
                       variable=self.orientation_var).grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Настройки изображения
        ttk.Label(settings_frame, text="Настройки изображения:", 
                 font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        # Яркость
        ttk.Label(settings_frame, text="Яркость:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.brightness_var = tk.DoubleVar(value=1.0)
        brightness_scale = ttk.Scale(settings_frame, from_=0.1, to=3.0, variable=self.brightness_var, 
                                   orient=tk.HORIZONTAL, command=self.on_settings_change)
        brightness_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.brightness_label = ttk.Label(settings_frame, text="1.0", width=4)
        self.brightness_label.grid(row=2, column=2, padx=(5, 0))
        
        # Контрастность
        ttk.Label(settings_frame, text="Контрастность:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.contrast_var = tk.DoubleVar(value=1.0)
        contrast_scale = ttk.Scale(settings_frame, from_=0.1, to=3.0, variable=self.contrast_var,
                                 orient=tk.HORIZONTAL, command=self.on_settings_change)
        contrast_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.contrast_label = ttk.Label(settings_frame, text="1.0", width=4)
        self.contrast_label.grid(row=3, column=2, padx=(5, 0))
        
        # Резкость
        ttk.Label(settings_frame, text="Резкость:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.sharpness_var = tk.DoubleVar(value=1.0)
        sharpness_scale = ttk.Scale(settings_frame, from_=0.1, to=3.0, variable=self.sharpness_var,
                                  orient=tk.HORIZONTAL, command=self.on_settings_change)
        sharpness_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.sharpness_label = ttk.Label(settings_frame, text="1.0", width=4)
        self.sharpness_label.grid(row=4, column=2, padx=(5, 0))
        
        # Качество
        ttk.Label(settings_frame, text="Качество JPEG:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.quality_var = tk.IntVar(value=75)
        quality_scale = ttk.Scale(settings_frame, from_=10, to=100, variable=self.quality_var,
                                orient=tk.HORIZONTAL, command=self.update_quality_label)
        quality_scale.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.quality_label = ttk.Label(settings_frame, text="75", width=4)
        self.quality_label.grid(row=5, column=2, padx=(5, 0))
        
        # Кнопки сброса
        ttk.Button(settings_frame, text="Сбросить настройки", 
                  command=self.reset_settings).grid(row=6, column=1, pady=(10, 0))
        
        # Прогресс бар
        ttk.Label(main_frame, text="Прогресс:").grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(main_frame, text="Готов к работе")
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Кнопка конвертации
        self.convert_button = ttk.Button(main_frame, text="Конвертировать в черно-белый", 
                                       command=self.start_conversion, state=tk.DISABLED)
        self.convert_button.grid(row=7, column=0, columnspan=3, pady=15)
    
    def update_brightness_label(self, value):
        """Обновление метки яркости"""
        self.brightness_label.config(text=f"{float(value):.1f}")
    
    def update_contrast_label(self, value):
        """Обновление метки контрастности"""
        self.contrast_label.config(text=f"{float(value):.1f}")
    
    def update_sharpness_label(self, value):
        """Обновление метки резкости"""
        self.sharpness_label.config(text=f"{float(value):.1f}")
    
    def update_quality_label(self, value):
        """Обновление метки качества"""
        self.quality_label.config(text=f"{int(float(value))}")
    
    def on_settings_change(self, value):
        """Обработчик изменения настроек для реального времени"""
        self.update_brightness_label(self.brightness_var.get())
        self.update_contrast_label(self.contrast_var.get())
        self.update_sharpness_label(self.sharpness_var.get())
        self.update_preview()
    
    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.sharpness_var.set(1.0)
        self.quality_var.set(75)
        self.on_settings_change(None)
    
    def browse_file(self):
        """Выбор PDF файла"""
        filename = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            self.input_file = filename
            self.file_label.config(text=os.path.basename(filename), foreground="black")
            self.convert_button.config(state=tk.NORMAL)
            self.status_label.config(text="Файл выбран, загрузка предпросмотра...")
            
            # Загружаем информацию о PDF
            try:
                doc = fitz.open(filename)
                self.total_pages = len(doc)
                self.current_page = 0
                doc.close()
                
                # Обновляем спинбокс страниц
                self.page_spinbox.config(from_=1, to=max(1, self.total_pages))
                self.page_var.set("1")
                
                # Загружаем предпросмотр
                self.load_preview()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить PDF: {str(e)}")
    
    def load_preview(self):
        """Загружает предпросмотр в отдельном потоке"""
        def load_thread():
            try:
                page_num = int(self.page_var.get()) - 1
                preview_image = self.converter.get_preview_image(self.input_file, page_num)
                
                if preview_image:
                    self.original_preview = preview_image.copy()
                    self.root.after(0, self.update_preview_image)
                    
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Ошибка загрузки: {str(e)}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_preview(self):
        """Обновляет предпросмотр с текущими настройками"""
        if self.original_preview is None:
            self.load_preview()
            return
        
        try:
            # Применяем текущие настройки к изображению
            enhanced_image = self.converter.apply_preview_enhancements(
                self.original_preview.copy(),
                self.brightness_var.get(),
                self.contrast_var.get(),
                self.sharpness_var.get()
            )
            
            # Конвертируем для Tkinter
            photo = ImageTk.PhotoImage(enhanced_image)
            
            # Обновляем изображение
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo  # Сохраняем ссылку
            
        except Exception as e:
            print(f"Ошибка обновления предпросмотра: {e}")
    
    def update_preview_image(self):
        """Обновляет основное изображение предпросмотра"""
        if self.original_preview:
            self.update_preview()
            self.status_label.config(text="Предпросмотр загружен. Настройте параметры.")
    
    def update_progress(self, value, message):
        """Обновление прогресса конвертации"""
        self.progress_var.set(value)
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_conversion(self):
        """Запуск процесса конвертации"""
        if not self.input_file:
            messagebox.showerror("Ошибка", "Сначала выберите PDF файл")
            return
        
        # Получаем настройки из интерфейса
        self.converter.set_output_size(
            self.size_var.get(), 
            self.orientation_var.get()
        )
        
        self.converter.set_image_settings(
            brightness=self.brightness_var.get(),
            contrast=self.contrast_var.get(),
            sharpness=self.sharpness_var.get(),
            quality=self.quality_var.get()
        )
        
        # Выбираем место для сохранения
        output_file = filedialog.asksaveasfilename(
            title="Сохранить черно-белый PDF как",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
        
        # Блокируем кнопку во время конвертации
        self.convert_button.config(state=tk.DISABLED)
        
        # Запускаем конвертацию в отдельном потоке
        def conversion_thread():
            try:
                success = self.converter.convert_pdf_to_bw(
                    self.input_file, 
                    output_file,
                    progress_callback=self.update_progress
                )
                
                self.root.after(0, lambda: self.conversion_finished(success, output_file))
                
            except Exception as e:
                self.root.after(0, lambda: self.conversion_finished(False, None, str(e)))
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def conversion_finished(self, success, output_file=None, error_msg=None):
        """Обработчик завершения конвертации"""
        if success:
            messagebox.showinfo("Успех", f"Конвертация завершена успешно!\nФайл сохранен как: {output_file}")
            self.status_label.config(text="Конвертация завершена")
        else:
            if error_msg:
                messagebox.showerror("Ошибка", f"Произошла ошибка при конвертации: {error_msg}")
                self.status_label.config(text=f"Ошибка: {error_msg}")
            else:
                messagebox.showerror("Ошибка", "Произошла ошибка при конвертации")
                self.status_label.config(text="Ошибка конвертации")
        
        self.convert_button.config(state=tk.NORMAL)
        self.progress_var.set(0)