import platform
import subprocess
import threading
import time
import tkinter as tk
import random
import requests


class GetText:
    def __init__(self):
        self.url = "https://www.lipsum.com/feed/json?amount={amount}&what=words&start=yes"

    def get_text(self):
        # Generate a random amount of words and fetch lorem text from the API
        amount = random.randint(100, 200)
        url = self.url.format(amount=str(amount))
        response = requests.get(url)
        data = response.json()
        lorem_text = data["feed"]["lipsum"]
        words = lorem_text.split(" ")
        if len(words) > amount:
            lorem_text = ' '.join(words[:amount]) + "."
        return lorem_text


class Typing:
    def __init__(self, target_text):
        self.target_text = target_text
        self.errors = 0
        self.correct = 0

    def check_errors(self, entered_text):
        # Compare entered text with target text and count errors
        for i, (c1, c2) in enumerate(zip(entered_text, self.target_text)):
            if c1 != c2 and c1 != "":
                self.errors += 1
            elif c1 == c2:
                self.correct += 1


class Display(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('500x200')
        self.configure(background="#EBFFC5")
        self.text = GetText()
        self.set_window()
        self.title = "Speedy Typing McQueen"
        self.timer_running = False
        self.timer_thread, self.label_text, self.timer_label, self.start_button, self.text_box, \
            self.start_check, self.typing, self.label, \
            self.button, self.button = None, None, None, None, None, None, None, None, None, None
        self.start_time = 0

    def start(self):
        # Destroy the start button and get screen size
        global screensize
        self.button.destroy()
        if platform.system() == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        else:
            result = subprocess.run(['xrandr'], stdout=subprocess.PIPE)
            output = result.stdout.decode('utf-8')
            lines = output.splitlines()
            for line in lines:
                if ' connected' in line:
                    parts = line.split()
                    for part in parts:
                        if 'x' in part:
                            screensize = tuple(map(int, part.split('x')))
                            break
        self.geometry(f'{screensize[0]}x{screensize[1]}')
        self.timer_running = False
        wrap_length = self.winfo_width() + 1000
        text = self.text.get_text()

        self.label_text = tk.Label(self, text=text, font=("Arial", 15, "bold"), bg="#EBFFC5", wraplength=wrap_length)
        self.label_text.pack(padx=4, pady=4, side=tk.TOP)
        self.timer_label = tk.Label(self, text="Time remaining: 30", font=("Arial", 15, "bold"), bg="#FFFFFF")
        self.timer_label.pack(padx=4, pady=4, side=tk.TOP)
        self.start_button = tk.Button(self, text="Start timer", font=("Arial", 15, "bold"), bg="#FFFFFF",
                                      command=lambda: self.start_typing(text), width=10)
        self.start_button.pack(padx=4, pady=4, side=tk.TOP)
        self.text_box = tk.Text(self, font=("Arial", 15, "bold"), bg="#FFFFFF", height=20)
        self.text_box.pack(padx=4, pady=4, side=tk.TOP)
        self.start_check = tk.Button(self, text="Check", font=("Arial", 15, "bold"), bg="#FFFFFF",
                                     command=self.check, width=10)
        self.start_check.pack(padx=4, pady=4, side=tk.TOP)

    def start_typing(self, text, num=0):
        # Start the timer and initiate Typing class when the user starts typing
        if num == 0:
            self.start_time = time.time()
            self.typing = Typing(text)
            if not self.timer_running:
                self.timer_running = True
                self.timer_thread = threading.Thread(target=self.run_timer)
                self.timer_thread.start()
        else:
            self.update_display(new_text=text)

    def update_display(self, new_text):
        # Update display with new text and reset button command
        self.text_box.delete("1.0", tk.END)
        self.label_text.configure(text=new_text)
        self.start_button.configure(command=lambda: self.start_typing(new_text))

    def start_typing_multiple(self, text):
        # Start typing with new text
        self.typing = Typing(text)
        if not self.timer_running:
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.start()

    def run_timer(self):
        # Run the timer for 30 seconds
        for i in range(30, 0, -1):
            time.sleep(1)
            if not self.timer_running:
                return
            self.timer_label.config(text=f"Time remaining: {i}")
        self.timer_running = False
        self.check()

    def check(self):
        # Check the user's typing performance
        if self.timer_running:
            self.timer_running = False
            self.timer_thread.join()  # Wait for the timer thread to finish
        entered_text = self.text_box.get('1.0', tk.END)
        self.typing.check_errors(entered_text)
        errors = self.typing.errors - 1
        correct = self.typing.correct
        time_taken = 0.5
        words_per_minute = correct / time_taken
        result_text = f"Errors: {errors}, Correct: {correct}, in {30} seconds\n Your total speed is {words_per_minute} WPM"
        self.timer_label.config(text=f"{result_text}")
        text = self.text.get_text()
        self.update_display(new_text=text)

    def set_window(self):
        # Set up the initial window with a label, button, and other UI elements

        self.label = tk.Label(self, text="Speedy Typing McQueen", font=("Arial", 30, "bold"), bg="#EBFFC5")
        self.label.pack(padx=4, pady=4, side=tk.TOP)
        self.button = tk.Button(self, text="Start", font=("Arial", 15, "bold"), bg="#EBFFC5", command=self.start)
        self.button.pack(padx=4, pady=4, side=tk.TOP)


def main():
    # Create and run the display
    display = Display()
    display.mainloop()


if __name__ == "__main__":
    main()
