import tkinter as tk

root = tk.Tk()
label = tk.Label(root, text="gridテスト", bg="cyan", fg="black", font=("Arial", 24))
label.grid(row=0, column=0, padx=50, pady=50)
root.mainloop()