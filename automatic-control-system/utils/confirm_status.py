import tkinter as tk
from tkinter import ttk

import pandas as pd


def show_data_and_wait_for_confirm(data):
    """Display station data in a Tk window and block until the user confirms."""

    def on_confirm():
        """Close the confirmation window."""
        print("The confirm button was clicked. Closing the window.")
        root.destroy()

    root = tk.Tk()
    root.title("Station Information")

    font_style = ("Microsoft YaHei", 10)

    # Render one frame per station so the current state is easy to scan.
    row = 0
    for station, info in data.items():
        frame = tk.Frame(root, borderwidth=2, relief="groove")
        frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

        station_label = tk.Label(frame, text=station, font=font_style, fg="blue")
        station_label.pack(padx=5, pady=5, anchor="w")

        info_text = tk.Text(
            frame,
            wrap=tk.WORD,
            height=1,
            font=font_style,
            borderwidth=0,
            background=frame.cget("background"),
        )
        info_text.pack(padx=5, pady=2, fill="both", expand=True)
        for key, value in info.items():
            info_text.insert(tk.END, f"{key}: {value}\n")
        info_text.configure(state="disabled")
        info_text.configure(height=info_text.count("1.0", "end", "lines")[0])

        row += 1

    confirm_button = tk.Button(root, text="Confirm", font=font_style, command=on_confirm)
    confirm_button.grid(row=row, column=0, pady=10)

    root.mainloop()


def display_excel_data(dataframe):
    """Display a pandas DataFrame in a Tkinter table view."""

    def on_confirm():
        """Close the DataFrame window."""
        print("The confirm button was clicked. Closing the window.")
        root.destroy()

    root = tk.Tk()
    root.title("Excel Data Display")

    font_style = ("Microsoft YaHei", 10)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    columns = [str(col) for col in dataframe.columns]
    tree = ttk.Treeview(main_frame, columns=columns, show="headings")

    hscrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(xscroll=hscrollbar.set)
    hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    vscrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=vscrollbar.set)
    vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    for column in columns:
        tree.heading(column, text=column)
        max_width = max(
            [len(str(value)) for value in dataframe[column].fillna("")] + [len(column)]
        )
        column_width = max(max_width * 10, 50)
        tree.column(column, width=column_width)

    for _, row in dataframe.iterrows():
        tree.insert("", tk.END, values=list(row))

    confirm_button = tk.Button(
        main_frame, text="Confirm", font=font_style, command=on_confirm
    )
    confirm_button.pack(side=tk.BOTTOM, pady=10)

    root.mainloop()
