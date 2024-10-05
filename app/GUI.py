from time import sleep
import os
import customtkinter as ctk
import tkinter.messagebox as mb
from typing import List, Dict, Any, Optional
from .ProjectLoader import get_text_from_project, apply_translations_to_project
from .FileStorage import save_data, load_data
from .Translator import translate_texts
from .QueryManager import QueryManager
from .FasterScrolling import FastScrollableFrame
from .GrowingTextBox import GrowingTextBox
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
class TranslationApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.queryManager: QueryManager = QueryManager()
        self.selected_path: Optional[str] = None
        self.data: List[Dict[str, Any]] = []
        self.current_file_info: Optional[Dict[str, Any]] = None
        self.display_start_index: int = 0
        self.display_end_index: int = 0
        self.display_texts: List[Dict[str, Any]] = []
        self.auto_mode: ctk.BooleanVar = ctk.BooleanVar(value=False)
        self.ignore_translated_var: ctk.BooleanVar = ctk.BooleanVar()
        self.green_filter_var: ctk.BooleanVar = ctk.BooleanVar()
        self.yellow_filter_var: ctk.BooleanVar = ctk.BooleanVar()
        self.red_filter_var: ctk.BooleanVar = ctk.BooleanVar()
        
        self.green_filter_var.set(True)
        self.yellow_filter_var.set(True)
        self.red_filter_var.set(True)

        self.x_pages_ahead_entry: ctk.CTkEntry = None
        self.search_entry: ctk.CTkEntry = None
        self.texts_count_entry: ctk.CTkEntry = None
        self.file_labels: Dict[str, ctk.CTkLabel] = {}

        self.title("RPG Maker Translator")
        self.geometry("1400x800")

        # Configure layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel
        self.left_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=0)

        # Top panel in the left panel with buttons
        self.top_left_frame: ctk.CTkFrame = ctk.CTkFrame(self.left_frame)
        self.top_left_frame.grid_columnconfigure(0, weight=1)
        self.top_left_frame.grid_columnconfigure(1, weight=1)
        self.top_left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.select_directory_button: ctk.CTkButton = ctk.CTkButton(
            self.top_left_frame, text="Select Directory", command=self.select_directory
        )
        self.select_directory_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.save_progress_button: ctk.CTkButton = ctk.CTkButton(
            self.top_left_frame, text="Save Progress", command=self.save_progress
        )
        self.save_progress_button.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Scrollable frame for JSON files
        self.scrollable_frame: FastScrollableFrame = FastScrollableFrame(self.left_frame, width=250)
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Apply translation button
        self.apply_translation_button: ctk.CTkButton = ctk.CTkButton(self.left_frame, text="Apply Translation", command=self.apply_translation)
        self.apply_translation_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Right panel
        self.right_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nswe")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(2, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=0)

        # Top Right Frame
        self.top_right_frame: ctk.CTkFrame = ctk.CTkFrame(self.right_frame)
        self.top_right_frame.grid(row=0, column=0, columnspan=3, sticky="nswe", pady=10, padx=10)
        self.top_right_frame.grid_columnconfigure(0, weight=1)
        self.top_right_frame.grid_columnconfigure(1, weight=1)

        # Translation-related widgets (Top-left section)
        self.translate_frame = ctk.CTkFrame(self.top_right_frame)
        self.translate_frame.grid_columnconfigure(0, weight=1)
        self.translate_frame.grid_columnconfigure(1, weight=0)
        self.translate_frame.grid_columnconfigure(2, weight=1)
        self.translate_frame.grid_rowconfigure(0, weight=1)
        self.translate_frame.grid_rowconfigure(1, weight=0)
        self.translate_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.translate_button: ctk.CTkButton = ctk.CTkButton(
            self.translate_frame,
            text="Translate",
            command=self.translate_texts,
        )
        self.translate_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)

        self.auto_toggle_button: ctk.CTkCheckBox = ctk.CTkCheckBox(
            self.translate_frame,
            text="Auto",
            variable=self.auto_mode,
            command=self.toggle_auto_mode
        )
        self.auto_toggle_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.x_pages_ahead_label: ctk.CTkLabel = ctk.CTkLabel(self.translate_frame, text="Pages Ahead:")
        self.x_pages_ahead_label.grid(row=1, column=1, padx=10, sticky="e")
        self.x_pages_ahead_entry: ctk.CTkEntry = ctk.CTkEntry(self.translate_frame, width=50)
        self.x_pages_ahead_entry.insert(0, "1") 
        self.x_pages_ahead_entry.grid(row=1, column=2, padx=10,pady=10, sticky="nsew")

        # Filtering-related widgets (Top-right section)
        self.filter_frame = ctk.CTkFrame(self.top_right_frame)
        self.filter_frame.grid_columnconfigure(0, weight=1)
        self.filter_frame.grid_columnconfigure(1, weight=1)
        self.filter_frame.grid_columnconfigure(2, weight=1)
        self.filter_frame.grid_columnconfigure(3, weight=1)
        self.filter_frame.grid_rowconfigure(0, weight=1)
        self.filter_frame.grid_rowconfigure(1, weight=1)
        self.filter_frame.grid_rowconfigure(2, weight=1)
        self.filter_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Displayed Texts count and search
        self.texts_count_label: ctk.CTkLabel = ctk.CTkLabel(self.filter_frame, text="Displayed Texts:")
        self.texts_count_label.grid(row=0, column=0, padx=10, sticky="e")
        self.texts_count_entry: ctk.CTkEntry = ctk.CTkEntry(self.filter_frame, width=50)
        self.texts_count_entry.insert(0, "50")
        self.texts_count_entry.grid(row=0, column=1, padx=10, sticky="nsew", pady=10)

        self.search_entry: ctk.CTkEntry = ctk.CTkEntry(self.filter_frame, width=200, placeholder_text="Search...")
        self.search_entry.grid(row=0, column=2, padx=10, sticky="nsew", pady=10, columnspan=2)

        # Reload button (Bottom section)
        self.reload_button: ctk.CTkButton = ctk.CTkButton(self.filter_frame, text="Reload", command=self.reload_texts)
        self.reload_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.clear_translated_texts_button: ctk.CTkButton = ctk.CTkButton(self.filter_frame, text="Clear Translated Texts", command=self.clear_translated_texts)
        self.clear_translated_texts_button.grid(row=2, column=2, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Ignore Translated checkbox
        self.ignore_translated_checkbox: ctk.CTkCheckBox = ctk.CTkCheckBox(
            self.filter_frame,
            text="Ignore Translated",
            variable=self.ignore_translated_var
        )
        self.ignore_translated_checkbox.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Green, Yellow, and Red filter checkboxes
        self.green_toggle: ctk.CTkCheckBox = ctk.CTkCheckBox(self.filter_frame, text="Green", variable=self.green_filter_var)
        self.green_toggle.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")

        self.yellow_toggle: ctk.CTkCheckBox = ctk.CTkCheckBox(self.filter_frame, text="Yellow", variable=self.yellow_filter_var)
        self.yellow_toggle.grid(row=1, column=2, padx=5, pady=10, sticky="nsew")

        self.red_toggle: ctk.CTkCheckBox = ctk.CTkCheckBox(self.filter_frame, text="Red", variable=self.red_filter_var)
        self.red_toggle.grid(row=1, column=3, padx=5, pady=10, sticky="nsew")

        # Scrollable frame for texts
        self.text_scrollable_frame: FastScrollableFrame = FastScrollableFrame(self.right_frame)
        self.text_scrollable_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nswe")

        # Previous and Next buttons for navigating texts
        self.prev_button: ctk.CTkButton = ctk.CTkButton(self.right_frame, text="Prev", command=self.prev_texts)
        self.prev_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.text_index_label_var: ctk.StringVar = ctk.StringVar()
        self.text_index_label: ctk.CTkLabel = ctk.CTkLabel(self.right_frame, textvariable=self.text_index_label_var, width=100, height=30, fg_color="gray")
        self.text_index_label.grid(row=2, column=1, padx=10, pady=10, sticky="ns")

        self.next_button: ctk.CTkButton = ctk.CTkButton(self.right_frame, text="Next", command=self.next_texts)
        self.next_button.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)




    def select_directory(self) -> None:
        if self.selected_path:
            response = self.prompt_save_progress()
            if response == mb.YES:
                self.save_progress()
        self.selected_path = ctk.filedialog.askdirectory()
        if self.selected_path:
            print(f"Selected directory: {self.selected_path}")
            self.data = load_data(self.selected_path)
            if not self.data:
                self.data = get_text_from_project(self.selected_path)

            # Clear existing widgets in the scrollable frame
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Ensure the scrollable frame's grid is properly configured
            self.scrollable_frame.grid_columnconfigure(0, weight=1)  # Ensure the main column expands properly

            # Iterate over the data and create file buttons and labels
            for file_info in self.data:
                file_name = os.path.basename(file_info['json_file'])
                num_texts = file_info['num_texts']
                num_translated = file_info['num_translated']

                # Create a frame for each file's entry
                file_frame = ctk.CTkFrame(self.scrollable_frame)
                file_frame.grid_columnconfigure(0, weight=2)  # File button column (larger weight)
                file_frame.grid_columnconfigure(1, weight=1)  # Label column for text counts (smaller weight)
                file_frame.grid(sticky="ew", padx=5, pady=5)

                # Create the file button (left) with fixed width
                file_button = ctk.CTkButton(file_frame, text=file_name, command=lambda f=file_info: self.display_file(f))
                file_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

                # Create the label showing translation progress (right) with fixed width and more padding
                num_texts_label = ctk.CTkLabel(
                    file_frame, text=f"{num_translated}/{num_texts}",
                )
                num_texts_label.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

                # Store reference to the label for updates
                self.file_labels[file_info['json_file']] = num_texts_label


    def display_file(self, file_info: Dict[str, Any]) -> None:
        self.save_texts()
        self.current_file_info = file_info
        self.display_start_index = 0
        self.queryManager.load_dataset(file_info['texts'], self.ignore_translated_var.get(), self.search_entry.get(), self.red_filter_var.get(), self.yellow_filter_var.get(), self.green_filter_var.get())
        self.display_text(self.display_start_index)

    def display_text(self, start_index: int = 0) -> None:
        num_texts: int = int(self.texts_count_entry.get()) if self.texts_count_entry.get().isdigit() else 50
        self.display_texts, self.display_start_index, self.display_end_index = self.queryManager.get_texts(start_index, num_texts)
        current_widget_count: int = len(self.text_scrollable_frame.winfo_children())
        self.run_auto_translation()

        if current_widget_count > num_texts:
            for widget in self.text_scrollable_frame.winfo_children()[num_texts:]:
                widget.destroy()

        for i in range(current_widget_count, num_texts):
            text_frame = ctk.CTkFrame(self.text_scrollable_frame)

            original_textbox = GrowingTextBox(text_frame, height=5)
            original_textbox.configure(state="disabled")

            copy_button = ctk.CTkButton(text_frame, text="C", width=30)

            translated_textbox = GrowingTextBox(text_frame, height=5)

            split_button = ctk.CTkButton(text_frame, text="+", width=30)

            # Add a label to display the key
            key_label = ctk.CTkLabel(text_frame, text="", width=100)

            text_frame.grid_columnconfigure(0, weight=1)
            text_frame.grid_columnconfigure(1, weight=0)
            text_frame.grid_columnconfigure(2, weight=1)
            text_frame.grid_columnconfigure(3, weight=0)
            text_frame.grid_columnconfigure(4, weight=0)  # Add space for key label

            text_frame.pack(fill="x", padx=5, pady=5)
            original_textbox.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            copy_button.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
            translated_textbox.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
            split_button.grid(row=0, column=3, padx=10, pady=5, sticky="nsew")
            key_label.grid(row=0, column=4, padx=10, pady=5, sticky="nsew")  # Grid for the key label

            self.update_idletasks()

        for i, text in enumerate(self.display_texts):
            text_frame = self.text_scrollable_frame.winfo_children()[i]
            original_textbox = text_frame.winfo_children()[0]
            copy_button = text_frame.winfo_children()[1]
            translated_textbox = text_frame.winfo_children()[2]
            split_button = text_frame.winfo_children()[3]
            key_label = text_frame.winfo_children()[4]

            original_textbox.configure(state="normal")
            original_textbox.delete("1.0", "end")
            original_textbox.insert("1.0", text['orig'])
            original_textbox.configure(state="disabled")

            translated_textbox.delete("1.0", "end")
            translated_textbox.insert("1.0", text['trans'])
            
            # Display the key from the text object
            key_label.configure(text=text['key'])

            # Check what the ['color'] field is set to and set the background color accordingly
            # if 'color' does not exist, set the background to white
            if 'color' in text:
                self.mark_text_color(translated_textbox, text['color'])
            else:
                self.mark_text_color(translated_textbox, 'white')

            def copy_text(t, trans_textbox: GrowingTextBox) -> None:
                self.clipboard_clear()
                self.clipboard_append(t['orig'])
                trans_textbox.delete("1.0", "end")
                trans_textbox.insert("1.0", t['orig'])
                t['trans'] = t['orig']
                

            copy_button.configure(command=lambda t=text, otb=translated_textbox: copy_text(t, otb))
            split_button.configure(command=lambda t=i: self.split_text(t))

        # Clear the remaining widgets if there are fewer texts than before
        for i in range(len(self.display_texts), num_texts):
            text_frame = self.text_scrollable_frame.winfo_children()[i]
            original_textbox = text_frame.winfo_children()[0]
            copy_button = text_frame.winfo_children()[1]
            translated_textbox = text_frame.winfo_children()[2]
            split_button = text_frame.winfo_children()[3]
            key_label = text_frame.winfo_children()[4]

            original_textbox.configure(state="normal")
            original_textbox.delete("1.0", "end")
            original_textbox.configure(state="disabled")

            # Set color to white
            self.mark_text_color(translated_textbox, 'white')
            
            translated_textbox.delete("1.0", "end")
            copy_button.configure(command=None)
            split_button.configure(command=None)
            key_label.configure(text="")  # Clear the key label

        self.text_index_label_var.set(f"{self.display_start_index} - {self.display_end_index}")

    def save_progress(self) -> None:
        #check if a directory has been selected
        if not self.selected_path:
            return
        self.save_texts()
        # count the number of translated texts in each file
        for file_info in self.data:
             file_info['num_translated'] = sum(1 for text in file_info['texts'] if text.get('trans'))
             self.file_labels[file_info['json_file']].configure(text=str(file_info['num_translated']) + "/" + str(file_info['num_texts']))
        save_data(self.data, self.selected_path)
        pass

    def save_texts(self) -> None:
        if self.directory_selected():
            translated_texts: List[str] = []
            for widget in self.text_scrollable_frame.winfo_children():
                translated_text = widget.winfo_children()[2].get("1.0", "end-1c")
                translated_texts.append(translated_text)
            self.queryManager.update_texts(self.display_start_index, self.display_end_index, translated_texts)

    def translate_texts(self) -> None:
        if not self.auto_mode.get():
            self.translate_button.configure(state="disabled")
        self.save_texts()
        self.translate_texts_for_range(self.display_start_index, self.display_end_index)

    def reload_texts(self) -> None:
        self.save_texts()
        self.queryManager.load_dataset(self.current_file_info['texts'], self.ignore_translated_var.get(), self.search_entry.get(), self.red_filter_var.get(), self.yellow_filter_var.get(), self.green_filter_var.get())
        self.display_start_index = 0
        self.display_end_index = 0
        for widget in self.text_scrollable_frame.winfo_children():
            widget.destroy()
        self.display_text(self.display_start_index)

    def next_texts(self) -> None:
        self.save_texts()
        # Calculate the next page index
        if self.display_end_index < len(self.current_file_info['texts']):
            next_page_start = self.display_end_index

            # Display the next page
            self.display_text(next_page_start)

    def prev_texts(self) -> None:
        self.save_texts()
        if self.display_start_index - int(self.texts_count_entry.get()) >= 0:
            self.display_text(self.display_start_index - int(self.texts_count_entry.get()))

    def split_text(self, index: int) -> None:
        #save whatever the user has done
        self.save_texts()
        #if the last element in display texts trans is empty
        if self.display_texts[-1]['trans'] == '':
            #shift all elements after index down by 1
            for i in range(len(self.display_texts)-1, index, -1):
                self.display_texts[i]['trans'] = self.display_texts[i-1]['trans']
            #set the text at index to empty
            self.display_texts[index]['trans'] = ''
        #display the new texts
        self.refresh_display_texts()
        #save whatever the new texts are
        self.save_texts()
                
    def apply_translation(self) -> None:
        self.save_texts()
        self.save_progress()
        apply_translations_to_project(self.data)

    def toggle_auto_mode(self) -> None:
            """Toggles the Auto mode and enables or disables the translate button."""
            if self.auto_mode.get():
                # Disable the translate button if auto mode is on
                self.translate_button.configure(state="disabled")
                
                # Translate the current page and "x pages ahead" if in auto mode
                if self.directory_selected() and self.current_file_info:
                    diff = int(self.texts_count_entry.get())
                    for i in range(int(self.x_pages_ahead_entry.get()) + 1):
                        self.translate_texts_for_range(self.display_start_index + i*(diff), self.display_end_index + i*(diff))
            else:
                # Re-enable the translate button when auto mode is off
                self.translate_button.configure(state="normal")
                
    def translate_texts_for_range(self, start_index: int, end_index: int) -> None:
        """Translates the texts for the given range."""
        
        def run_translation():
            try:
                # Get texts for the given range
                texts_to_translate, _, _ = self.queryManager.get_texts(start_index, end_index - start_index)
                
                # Filter out texts that are already translated or currently being translated
                texts_to_translate = [
                    text for text in texts_to_translate
                    if not text['trans'] and not text.get('in_progress', False)
                ]
                
                if(self.auto_mode.get()):
                    # Filter out texts that are already auto translated
                    texts_to_translate = [
                        text for text in texts_to_translate
                        if not text.get('auto_translated', False)
                    ]
                    for text in texts_to_translate:
                        text['auto_translated'] = True
                
                # If no texts to translate, exit
                if len(texts_to_translate) == 0:
                    return
                
                # Mark the texts as 'in progress' to prevent duplicate translation requests
                for text in texts_to_translate:
                    text['in_progress'] = True
                
                # Perform the translation
                if texts_to_translate:
                    translate_texts(texts_to_translate)

                # Refresh the display with newly translated texts
                self.refresh_display_texts()
            
            finally:
                # Re-enable the translate button after translation is complete if not in auto mode
                if not self.auto_mode.get():
                    self.translate_button.configure(state="normal")
                
                # Mark the texts as no longer 'in progress'
                for text in texts_to_translate:
                    text['in_progress'] = False

        # Start the translation in a new thread
        if self.directory_selected() and self.current_file_info:
            translation_thread = threading.Thread(target=run_translation)
            translation_thread.start()
        else:
            self.translate_button.configure(state="normal")

    def run_auto_translation(self) -> None:
        """Runs the auto translation for the current page and pages ahead."""
        if self.auto_mode.get():
            try:
                diff: int = int(self.texts_count_entry.get())
            except ValueError:
                diff = 50

            next_translation_start = self.display_start_index
            if(next_translation_start >= len(self.current_file_info['texts'])):
                return
        
            # Translate the current and pages ahead
            for i in range(int(self.x_pages_ahead_entry.get()) + 1):
                #if we reached the end of the file, return
                if(next_translation_start + (i)*(diff) >= len(self.current_file_info['texts'])):
                    return
                self.translate_texts_for_range(next_translation_start + i*(diff), self.display_end_index + i*(diff))
                #flag nodes as auto translated

    def refresh_display_texts(self) -> None:
        """Refreshes the display texts in the current page."""
        for i, text in enumerate(self.display_texts):
            text_frame = self.text_scrollable_frame.winfo_children()[i]
            translated_textbox = text_frame.winfo_children()[2]
            translated_textbox.delete("1.0", "end")
            translated_textbox.insert("1.0", text['trans'])
            
            if 'color' in text:
                self.mark_text_color(translated_textbox, text['color'])
                
    def mark_text_color(self, translated_textbox: GrowingTextBox, color: str) -> None:
        """Marks the text box with the given color."""
        if color == 'red':
            translated_textbox.configure(bg="#FFC1C1")  # Soft/pastel red
        elif color == 'yellow':
            translated_textbox.configure(bg="#FFFACD")  # Soft/pastel yellow (light lemon)
        elif color == 'green':
            translated_textbox.configure(bg="#C1E1C1")  # Soft/pastel green (light mint)
        else:
            translated_textbox.configure(bg="white")
            
    def on_closing(self) -> None:
        """Handles the closing of the application."""
        # Ask the user if they want to save progress
        response = self.prompt_save_progress()
        
        if response is None:
            # If the user clicks "Cancel", do nothing and return
            return
        elif response:
            # If the user clicks "Yes", save progress and close
            self.save_progress()
            self.destroy()
        else:
            # If the user clicks "No", just close without saving
            self.destroy()
            
    def prompt_save_progress(self) -> None:
        return mb.askyesno("Save Progress", "Do you want to save your progress?")
        
    def directory_selected(self) -> bool:
        """Checks if a directory has been selected."""
        if not self.selected_path:
            mb.showerror("Error", "Please select a directory first.")
            return False
        return True
    
    def clear_translated_texts(self) -> None:
        """Clears all translated texts in the current page."""
        if not self.display_texts:
            return
        for i in range(len(self.display_texts)):
            text_frame = self.text_scrollable_frame.winfo_children()[i]
            translated_textbox = text_frame.winfo_children()[2]
            
            translated_textbox.delete("1.0", "end")