import tkinter as tk
from tkinter import ttk


def draw_text_field(
    parent, variable: tk.StringVar, title: str, default_value: str, width: int = 5
):
    frame = ttk.Frame(parent)
    field_title = ttk.Label(frame, text=title)
    field_title.grid(row=0, column=0)
    entry = ttk.Entry(frame)
    entry.configure(justify="center", textvariable=variable, width=width)
    entry.delete("0", "end")
    entry.insert("0", default_value)
    entry.grid(row=0, column=1, padx=10)
    frame.columnconfigure(0, weight=1)
    return frame


def draw_cm_number_field(
    parent, variable: tk.StringVar, title: str, default_value: str
):
    frame = ttk.Frame(parent)
    field_title = ttk.Label(frame, text=title)
    entry = ttk.Entry(
        frame, justify="center", textvariable=variable, validate="focusout", width=5
    )
    entry.delete("0", "end")
    entry.insert("0", default_value)
    text_cm = ttk.Label(frame, text="cm")
    # organize layout
    field_title.grid(row=0, column=0)
    entry.grid(row=0, column=1, padx=10)
    text_cm.grid(row=0, column=2)
    frame.columnconfigure(0, weight=1)
    return frame


def draw_button(parent, title, callback):
    button = ttk.Button(parent, text=title, command=callback)
    return button


def draw_icon_button(parent, icon, callback):
    button = ttk.Button(parent, image=icon, command=callback)
    return button


def draw_charuco_pattern_field(
    parent,
    rowVar: tk.StringVar,
    colVar: tk.StringVar,
    title: str,
    rowDefault: str,
    colDefault: str,
):
    frame = ttk.Frame(parent)

    frame_left = ttk.Frame(parent)
    label_title = ttk.Label(frame, text=title)
    label_title.grid(row=0, column=0)

    frame_right = ttk.Frame(frame)
    entry_row = ttk.Entry(frame_right, justify="center", textvariable=rowVar, width=3)
    entry_row.delete("0", "end")
    entry_row.insert("0", rowDefault)
    label_x = ttk.Label(frame_right, text="x")
    entry_column = ttk.Entry(
        frame_right, justify="center", textvariable=colVar, width=3
    )
    entry_column.delete("0", "end")
    entry_column.insert("0", colDefault)

    entry_row.grid(row=0, column=0)
    label_x.grid(row=0, column=1)
    entry_column.grid(row=0, column=2)
    # organize layout
    frame_left.grid(row=0, column=0)
    frame_right.grid(row=0, column=1, padx=10)

    return frame


def draw_refreshable_state_field(
    parent, title, icon, variable, default_value, callback
):
    frame = ttk.Frame(parent)
    label_title = ttk.Label(
        frame, compound="center", justify="center", padding=10, text=title
    )
    label_value = ttk.Label(frame, text=default_value, textvariable=variable)

    button = draw_icon_button(frame, icon, callback)

    label_title.grid(row=0, column=0)
    label_value.grid(row=0, column=1)
    button.grid(row=0, column=2, padx=10)

    return frame


def draw_state_field(parent, title, variable, default_value):
    frame = ttk.Frame(parent)
    label_title = ttk.Label(frame)
    label_title.configure(text=title)
    label_value = ttk.Label(frame, text=default_value, textvariable=variable)
    label_title.grid(row=0, column=0)
    label_value.grid(row=0, column=1, padx=10)

    return frame
