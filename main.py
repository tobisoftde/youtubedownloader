import pyperclip
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from pytube import YouTube
import threading
import time
import requests
import io

class YouTubeDownloaderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")

        # Fenstergröße und Position setzen
        window_width = 320
        window_height = 320
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = screen_width - window_width - 10  # 10 Pixel Abstand vom rechten Bildschirmrand
        y_position = screen_height - window_height - 75  # 10 Pixel Abstand vom unteren Bildschirmrand
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Hintergrundfarbe und Transparenz einstellen
        self.root.config(bg="#000000")  # Schwarzer Hintergrund
        self.root.attributes("-alpha", 0.8)  # Transparenz auf 80% setzen

        # Inhaltsrahmen
        self.content_frame = tk.Frame(self.root, bg="#000000")
        self.content_frame.place(relx=0.05, rely=0.5, anchor="w")

        # Label für den Titel
        self.title_label = tk.Label(self.content_frame, text="Video-Titel wird geladen...", font=("Helvetica", 10),
                                    bg="#000000", fg="#FFFFFF", wraplength=300)
        self.title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Label für das Thumbnail
        self.thumbnail_label = tk.Label(self.content_frame, bg="#000000")
        self.thumbnail_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Label für das Download-Format
        self.label = tk.Label(self.content_frame, text="Wähle das Download-Format:", font=("Helvetica", 12),
                              bg="#000000", fg="#FFFFFF")
        self.label.grid(row=2, column=0, pady=5, sticky="w")

        # Rahmen für die Buttons
        self.button_frame = tk.Frame(self.content_frame, bg="#000000")
        self.button_frame.grid(row=3, column=0, pady=5, sticky="w")

        # MP4 Button
        self.mp4_button = tk.Button(self.button_frame, text="MP4", command=lambda: self.select_format('mp4'), width=10,
                                    height=2, font=("Helvetica", 10), bg="#FFFFFF", fg="#000000")
        self.mp4_button.grid(row=0, column=0, padx=5, sticky="w")

        # MP3 Button
        self.mp3_button = tk.Button(self.button_frame, text="MP3", command=lambda: self.select_format('mp3'), width=10,
                                    height=2, font=("Helvetica", 10), bg="#FFFFFF", fg="#000000")
        self.mp3_button.grid(row=0, column=1, padx=5, sticky="w")

        self.root.withdraw()  # Fenster verstecken

        clipboard_checker = threading.Thread(target=self.check_clipboard_periodically)
        clipboard_checker.daemon = True  # Setze den Thread als Hintergrundthread
        clipboard_checker.start()  # Starte den Thread

    def get_video_title(self, url):
        try:
            yt = YouTube(url)
            return yt.title
        except Exception as e:
            print(f'Ein Fehler ist aufgetreten: {str(e)}')
            return "Fehler beim Abrufen des Titels"

    def get_thumbnail_url(self, url):
        try:
            yt = YouTube(url)
            return yt.thumbnail_url
        except Exception as e:
            print(f'Ein Fehler ist aufgetreten: {str(e)}')
            return None

    def download_video(self, url, format='mp4'):
        try:
            yt = YouTube(url)
            title = yt.title
            if format == 'mp4':
                video = yt.streams.get_highest_resolution()  # Höchste Auflösung wählen
                default_filename = video.default_filename
                print(f'Lade {default_filename} ({title}) als MP4 herunter...')
                video.download()
                print('Download abgeschlossen.')
            elif format == 'mp3':
                audio = yt.streams.filter(only_audio=True).first()
                default_filename = audio.default_filename
                print(f'Lade {default_filename} ({title}) als MP3 herunter...')
                audio.download()
                base, ext = os.path.splitext(default_filename)
                new_filename = base + '.mp3'
                os.rename(default_filename, new_filename)
                print('Download abgeschlossen.')
            self.hide_window()  # Verstecke das Fenster nach dem Download
        except Exception as e:
            print(f'Ein Fehler ist aufgetreten: {str(e)}')

    def get_youtube_url_from_clipboard(self):
        return pyperclip.paste()

    def select_format(self, format):
        url = self.get_youtube_url_from_clipboard()
        if not url.startswith("https://www.youtube.com/"):
            messagebox.showerror("Fehler", "Der kopierte Link ist nicht von YouTube.")
            return
        threading.Thread(target=self.download_video, args=(url, format)).start()

    def update_title_and_thumbnail(self):
        url = self.get_youtube_url_from_clipboard()
        if url.startswith("https://www.youtube.com/"):
            title = self.get_video_title(url)
            thumbnail_url = self.get_thumbnail_url(url)
            if thumbnail_url:
                image = self.download_thumbnail(thumbnail_url)
                if image:
                    self.title_label.config(text=title)
                    self.thumbnail_label.config(image=image)
                    self.thumbnail_label.image = image
                    self.root.deiconify()  # Fenster anzeigen

    def download_thumbnail(self, url):
        try:
            response = requests.get(url)
            image_data = Image.open(io.BytesIO(response.content))
            image_data = image_data.resize((280, 160))  # Thumbnail-Größe festlegen
            return ImageTk.PhotoImage(image_data)
        except Exception as e:
            print(f'Ein Fehler ist beim Herunterladen des Thumbnails aufgetreten: {str(e)}')
            return None

    def hide_window(self):
        self.root.withdraw()  # Verstecke das Fenster

    def check_clipboard_periodically(self):
        last_clipboard_content = None
        while True:
            clipboard_content = self.get_youtube_url_from_clipboard()
            if clipboard_content and clipboard_content.startswith("https://www.youtube.com/watch?v=") and clipboard_content != last_clipboard_content:
                last_clipboard_content = clipboard_content
                self.update_title_and_thumbnail()
            time.sleep(1)  # Warte 1 Sekunde zwischen den Prüfungen

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.root.mainloop()
