import tkinter as tk
import random


class Minesweeper:
    def __init__(self, root, width=10, height=10, num_mines=10):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.root = root
        self.root.title("Minesweeper")

        self.buttons = [[None for _ in range(width)] for _ in range(height)]
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.game_over = False
        self.create_widgets()
        self.place_mines()

    def create_widgets(self):
        for y in range(self.height):
            for x in range(self.width):
                button = tk.Button(self.root, text='', width=3, height=2,
                                   command=lambda x=x, y=y: self.reveal(x, y),
                                   relief=tk.RAISED, borderwidth=1)
                button.bind('<Button-3>', lambda e, x=x, y=y: self.toggle_flag(x, y))
                button.grid(row=y, column=x)
                self.buttons[y][x] = button

    def place_mines(self):
        while len(self.mines) < self.num_mines:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (x, y) not in self.mines:
                self.mines.add((x, y))

    def reveal(self, x, y):
        if self.game_over or (x, y) in self.revealed:
            return
        if (x, y) in self.mines:
            self.show_mines()
            self.buttons[y][x].config(text='*', background='red')
            self.game_over = True
            return
        mine_count = self.count_adjacent_mines(x, y)
        self.buttons[y][x].config(text=str(mine_count), relief=tk.SUNKEN)
        self.revealed.add((x, y))
        if mine_count == 0:
            for nx in range(x - 1, x + 2):
                for ny in range(y - 1, y + 2):
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.reveal(nx, ny)
        if len(self.revealed) == self.width * self.height - self.num_mines:
            self.show_success()

    def count_adjacent_mines(self, x, y):
        return sum((nx, ny) in self.mines for nx in range(x - 1, x + 2) for ny in range(y - 1, y + 2)
                   if 0 <= nx < self.width and 0 <= ny < self.height)

    def show_mines(self):
        for x, y in self.mines:
            self.buttons[y][x].config(text='*', background='red')

    def show_success(self):
        success_window = tk.Toplevel(self.root)
        success_window.title("Success")
        tk.Label(success_window, text="Success! You cleared the minefield.").pack(padx=20, pady=20)
        tk.Button(success_window, text="OK", command=self.root.quit).pack(pady=10)

    def toggle_flag(self, x, y):
        if self.game_over or (x, y) in self.revealed:
            return
        if (x, y) in self.flags:
            self.flags.remove((x, y))
            self.buttons[y][x].config(text='', background='SystemButtonFace')
        else:
            self.flags.add((x, y))
            self.buttons[y][x].config(text='F', background='yellow')


if __name__ == "__main__":
    root = tk.Tk()
    app = Minesweeper(root)
    root.mainloop()
