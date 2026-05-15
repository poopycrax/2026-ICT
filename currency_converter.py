from tkinter import *
from functools import partial
from datetime import date

# Exchange rates (update these as needed)
NZD_TO_VND = 14500   # 1 NZD = ~14,500 VND (approximate)
MAX_CALCS = 10


def round_to_2dp(value):
    return round(value, 2)


class Converter:

    def __init__(self):
        self.all_calculations_list = []

        self.main_frame = Frame(padx=10, pady=10)
        self.main_frame.grid()

        self.heading = Label(self.main_frame,
                             text="Currency Converter",
                             font=("Arial", "16", "bold"))
        self.heading.grid(row=0)

        instructions = ("Please enter the amount below and then press "
                        "one of the buttons to convert between "
                        "New Zealand Dollars (NZD) and Vietnamese Dong (VND).")
        self.instructions = Label(self.main_frame,
                                  text=instructions,
                                  wraplength=250, width=40,
                                  justify="left")
        self.instructions.grid(row=1)

        self.amount_entry = Entry(self.main_frame, font=("Arial", "14"))
        self.amount_entry.grid(row=2, padx=10, pady=10)

        self.answer_error = Label(self.main_frame,
                                  text="Please enter a number",
                                  fg="#004C99",
                                  font=("Arial", "14", "bold"))
        self.answer_error.grid(row=3)

        self.button_frame = Frame(self.main_frame)
        self.button_frame.grid(row=4)

        button_details_list = [
            ["To VND", "#009900", lambda: self.check_amount("to_vnd"), 0, 0],
            ["To NZD", "#990099", lambda: self.check_amount("to_nzd"), 0, 1],
            ["Help / Info", "#CC6600", self.to_help, 1, 0],
            ["History / Export", "#004C99", self.to_history, 1, 1]
        ]

        self.button_ref_list = []
        for item in button_details_list:
            btn = Button(self.button_frame,
                         text=item[0], bg=item[1],
                         fg="#FFFFFF", font=("Arial", "12", "bold"),
                         width=12, command=item[2])
            btn.grid(row=item[3], column=item[4], padx=5, pady=5)
            self.button_ref_list.append(btn)

        self.to_help_button = self.button_ref_list[2]
        self.to_history_button = self.button_ref_list[3]
        self.to_history_button.config(state=DISABLED)

    def check_amount(self, direction):
        to_convert = self.amount_entry.get()

        # Reset styling
        self.answer_error.config(fg="#004C99", font=("Arial", "13", "bold"))
        self.amount_entry.config(bg="#FFFFFF")

        has_errors = False

        try:
            to_convert = float(to_convert)
            if to_convert > 0:
                self.convert(direction, to_convert)
            else:
                has_errors = True
        except ValueError:
            has_errors = True

        if has_errors:
            self.answer_error.config(
                text="Please enter a number greater than 0",
                fg="#9C0000",
                font=("Arial", "10", "bold")
            )
            self.amount_entry.config(bg="#F4CCCC")
            self.amount_entry.delete(0, END)

    def convert(self, direction, amount):
        if direction == "to_vnd":
            result = round(amount * NZD_TO_VND)
            answer_statement = f"NZD ${amount:.2f} = ₫{result:,.0f} VND"
        else:
            result = round_to_2dp(amount / NZD_TO_VND)
            answer_statement = f"₫{amount:,.0f} VND = NZD ${result:.2f}"

        self.to_history_button.config(state=NORMAL)
        self.answer_error.config(text=answer_statement)
        self.all_calculations_list.append(answer_statement)

    def to_help(self):
        DisplayHelp(self)

    def to_history(self):
        HistoryExport(self, self.all_calculations_list)


class DisplayHelp:

    def __init__(self, partner):
        background = "#ffe6cc"
        self.help_box = Toplevel()
        self.help_box.title("Help / Info")

        partner.to_help_button.config(state=DISABLED)
        self.help_box.protocol("WM_DELETE_WINDOW",
                               partial(self.close_help, partner))

        self.help_frame = Frame(self.help_box, width=300, height=200)
        self.help_frame.grid()

        self.help_heading = Label(self.help_frame,
                                  text="Help / Info",
                                  font=("Arial", "14", "bold"))
        self.help_heading.grid(row=0)

        help_text = ("To use the program, enter the amount you wish to convert "
                     "and then press either 'To VND' to convert from New Zealand "
                     "Dollars to Vietnamese Dong, or 'To NZD' to convert the "
                     "other way.\n\n"
                     f"The exchange rate used is approximately "
                     f"1 NZD = {NZD_TO_VND:,} VND.\n\n"
                     "To see your calculation history and export it to a text "
                     "file, please click the 'History / Export' button.")

        self.help_text = Label(self.help_frame,
                               text=help_text,
                               wraplength=350,
                               justify="left")
        self.help_text.grid(row=1, padx=10)

        self.dismiss_button = Button(self.help_frame,
                                     font=("Arial", "12", "bold"),
                                     text="Dismiss", bg="#CC6600", fg="#FFFFFF",
                                     command=partial(self.close_help, partner))
        self.dismiss_button.grid(row=2, padx=10, pady=10)

        for widget in [self.help_frame, self.help_heading, self.help_text]:
            widget.config(bg=background)

    def close_help(self, partner):
        partner.to_help_button.config(state=NORMAL)
        self.help_box.destroy()


class HistoryExport:

    def __init__(self, partner, calculations):
        self.history_box = Toplevel()
        self.history_box.title("History / Export")

        partner.to_history_button.config(state=DISABLED)
        self.history_box.protocol("WM_DELETE_WINDOW",
                                  partial(self.close_history, partner))

        self.history_frame = Frame(self.history_box)
        self.history_frame.grid()

        if len(calculations) <= MAX_CALCS:
            calc_back = "#D5E804"
            calc_amount = "all your"
        else:
            calc_back = "#ffe6cc"
            calc_amount = (f"your recent calculations - "
                           f"showing {MAX_CALCS} / {len(calculations)}")

        recent_intro_txt = f"Below are {calc_amount} calculations."

        # Build display string (newest first)
        newest_first = list(reversed(calculations))
        display_list = newest_first[:MAX_CALCS]

        newest_first_string = "\n".join(display_list)

        export_instruction_txt = ("Press <Export> to save your calculations to a "
                                  "text file. If the file already exists, it will "
                                  "be overwritten.")

        history_labels_list = [
            ["History / Export", ("Arial", "16", "bold"), None],
            [recent_intro_txt, ("Arial", "11"), None],
            [newest_first_string, ("Arial", "14"), calc_back],
            [export_instruction_txt, ("Arial", "11"), None]
        ]

        history_label_ref = []
        for count, item in enumerate(history_labels_list):
            lbl = Label(self.history_box,
                        text=item[0], font=item[1], bg=item[2],
                        wraplength=300, justify="left", pady=10, padx=20)
            lbl.grid(row=count)
            history_label_ref.append(lbl)

        self.export_filename_label = history_label_ref[3]

        self.hist_button_frame = Frame(self.history_box)
        self.hist_button_frame.grid(row=4)

        button_details_list = [
            ["Export", "#004C99",
             lambda: self.export_data(calculations), 0, 0],
            ["Close", "#666666",
             partial(self.close_history, partner), 0, 1],
        ]

        for btn in button_details_list:
            Button(self.hist_button_frame,
                   font=("Arial", "12", "bold"),
                   text=btn[0], bg=btn[1], fg="#FFFFFF", width=12,
                   command=btn[2]).grid(row=btn[3], column=btn[4],
                                        padx=10, pady=10)

    def export_data(self, calculations):
        today = date.today()
        day = today.strftime("%d")
        month = today.strftime("%m")
        year = today.strftime("%Y")

        file_name = f"currency_conversions_{year}_{month}_{day}"
        write_to = f"{file_name}.txt"

        with open(write_to, "w") as text_file:
            text_file.write("***** Currency Conversions (NZD <-> VND) ******\n")
            text_file.write(f"Generated: {day}/{month}/{year}\n")
            text_file.write(f"Exchange rate used: 1 NZD = {NZD_TO_VND:,} VND\n\n")
            text_file.write("Calculation history (oldest to newest):\n")
            for item in calculations:
                text_file.write(item + "\n")

        success_string = (f"Export successful! File saved as {file_name}.txt")
        self.export_filename_label.config(
            fg="#009900", text=success_string,
            font=("Arial", "12", "bold"))

    def close_history(self, partner):
        partner.to_history_button.config(state=NORMAL)
        self.history_box.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title("NZD ↔ VND Currency Converter")
    Converter()
    root.mainloop()