from tkinter import *
from functools import partial
from datetime import date

# --- Constants ---
# Exchange rate: 1 NZD = approximately 14,500 VND (update as needed)
NZD_TO_VND = 14500

# Maximum number of calculations to display in the history window
MAX_CALCS = 10


def round_to_2dp(value):
    """Returns a float value rounded to 2 decimal places.
    Used when converting VND back to NZD to ensure clean dollar amounts."""
    return round(value, 2)


class Converter:
    """Main class that creates and manages the primary converter window.

    Handles the main GUI layout, user input, and coordinates with the
    DisplayHelp and HistoryExport classes via button commands.
    All calculation results are stored in all_calculations_list so they
    can be passed to the HistoryExport class when requested.
    """

    def __init__(self):
        # List to store every conversion result as a string for history/export
        self.all_calculations_list = []

        # Create the main frame with padding to keep widgets from touching edges
        self.main_frame = Frame(padx=10, pady=10)
        self.main_frame.grid()

        # Heading label displayed at the top of the window
        self.heading = Label(self.main_frame,
                             text="Currency Converter",
                             font=("Arial", "16", "bold"))
        self.heading.grid(row=0)

        # Instruction text to guide the user on how to use the program
        instructions = ("Please enter the amount below and then press "
                        "one of the buttons to convert between "
                        "New Zealand Dollars (NZD) and Vietnamese Dong (VND).")
        self.instructions = Label(self.main_frame,
                                  text=instructions,
                                  wraplength=250, width=40,
                                  justify="left")
        self.instructions.grid(row=1)

        # Entry field where the user types the amount they want to convert
        self.amount_entry = Entry(self.main_frame, font=("Arial", "14"))
        self.amount_entry.grid(row=2, padx=10, pady=10)

        # Label used to display both error messages and conversion results
        # Starts with a neutral prompt; updates dynamically based on user actions
        self.answer_error = Label(self.main_frame,
                                  text="Please enter a number",
                                  fg="#004C99",
                                  font=("Arial", "14", "bold"))
        self.answer_error.grid(row=3)

        # Frame to hold the four action buttons in a 2x2 grid layout
        self.button_frame = Frame(self.main_frame)
        self.button_frame.grid(row=4)

        # Button configuration list: [label, colour, command, row, column]
        # Using a list avoids repetitive Button() calls and keeps the code DRY
        button_details_list = [
            ["To VND", "#009900", lambda: self.check_amount("to_vnd"), 0, 0],
            ["To NZD", "#990099", lambda: self.check_amount("to_nzd"), 0, 1],
            ["Help / Info", "#CC6600", self.to_help, 1, 0],
            ["History / Export", "#004C99", self.to_history, 1, 1]
        ]

        # Create each button from the list above and store references for later use
        self.button_ref_list = []
        for item in button_details_list:
            btn = Button(self.button_frame,
                         text=item[0], bg=item[1],
                         fg="#FFFFFF", font=("Arial", "12", "bold"),
                         width=12, command=item[2])
            btn.grid(row=item[3], column=item[4], padx=5, pady=5)
            self.button_ref_list.append(btn)

        # Store specific button references so they can be enabled/disabled
        # when their corresponding popup windows are open or closed
        self.to_help_button = self.button_ref_list[2]
        self.to_history_button = self.button_ref_list[3]

        # History button starts disabled — only enabled after first conversion
        self.to_history_button.config(state=DISABLED)

    def check_amount(self, direction):
        """Validates the user's input before attempting a conversion.

        Retrieves the text from the entry field and checks:
        - That it can be converted to a float (not letters or symbols)
        - That the value is greater than zero (negative/zero amounts are invalid)

        If valid, passes the amount to the convert() method.
        If invalid, displays a red error message and highlights the entry field.

        Args:
            direction (str): Either "to_vnd" or "to_nzd" depending on which
                             button the user pressed.
        """
        to_convert = self.amount_entry.get()

        # Reset any previous error styling before re-validating
        self.answer_error.config(fg="#004C99", font=("Arial", "13", "bold"))
        self.amount_entry.config(bg="#FFFFFF")

        has_errors = False

        try:
            # Attempt to convert input string to a float
            to_convert = float(to_convert)
            if to_convert > 0:
                # Valid input — proceed with conversion
                self.convert(direction, to_convert)
            else:
                # Input is zero or negative — not a valid currency amount
                has_errors = True
        except ValueError:
            # Input could not be parsed as a number (e.g. letters, symbols)
            has_errors = True

        if has_errors:
            # Display error message in red and highlight the entry field pink
            self.answer_error.config(
                text="Please enter a number greater than 0",
                fg="#9C0000",
                font=("Arial", "10", "bold")
            )
            self.amount_entry.config(bg="#F4CCCC")
            # Clear the invalid entry so the user can type a new value
            self.amount_entry.delete(0, END)

    def convert(self, direction, amount):
        """Performs the currency conversion and updates the result label.

        Multiplies or divides the amount by the NZD_TO_VND exchange rate
        constant depending on the conversion direction. The result is
        formatted as a readable string and added to the calculations history.

        Args:
            direction (str): "to_vnd" converts NZD → VND;
                             "to_nzd" converts VND → NZD.
            amount (float): The validated positive number entered by the user.
        """
        if direction == "to_vnd":
            # Multiply NZD amount by exchange rate to get VND
            # round() removes decimal places since VND has no cents
            result = round(amount * NZD_TO_VND)
            answer_statement = f"NZD ${amount:.2f} = ₫{result:,.0f} VND"
        else:
            # Divide VND amount by exchange rate to get NZD
            # round_to_2dp() keeps the result to a standard dollar format
            result = round_to_2dp(amount / NZD_TO_VND)
            answer_statement = f"₫{amount:,.0f} VND = NZD ${result:.2f}"

        # Enable the history button now that at least one calculation exists
        self.to_history_button.config(state=NORMAL)

        # Display the result in the answer/error label
        self.answer_error.config(text=answer_statement)

        # Append the result string to the history list for later export
        self.all_calculations_list.append(answer_statement)

    def to_help(self):
        """Opens the Help/Info popup window by creating a DisplayHelp instance.
        Passes 'self' as the partner so the help window can re-enable this
        window's help button when it is closed."""
        DisplayHelp(self)

    def to_history(self):
        """Opens the History/Export popup window by creating a HistoryExport instance.
        Passes the full calculations list so the history window can display
        and export all previous conversions."""
        HistoryExport(self, self.all_calculations_list)


class DisplayHelp:
    """Creates a popup window that explains how to use the converter.

    Opened when the user clicks 'Help / Info'. Disables the help button
    on the main window while open to prevent multiple instances.
    The window can be closed via the Dismiss button or the window's X button.
    """

    def __init__(self, partner):
        """Sets up the help window layout and content.

        Args:
            partner: The Converter instance that opened this window.
                     Used to re-enable the help button on close.
        """
        background = "#ffe6cc"  # Orange tint background matching the help button colour

        # Create a new top-level window (child of the main window)
        self.help_box = Toplevel()
        self.help_box.title("Help / Info")

        # Disable the help button on the main window to prevent duplicate popups
        partner.to_help_button.config(state=DISABLED)

        # Bind the window's X (close) button to the close_help method
        # so the help button is always re-enabled when the window closes
        self.help_box.protocol("WM_DELETE_WINDOW",
                               partial(self.close_help, partner))

        # Frame inside the help window to hold all widgets
        self.help_frame = Frame(self.help_box, width=300, height=200)
        self.help_frame.grid()

        # Heading label for the help window
        self.help_heading = Label(self.help_frame,
                                  text="Help / Info",
                                  font=("Arial", "14", "bold"))
        self.help_heading.grid(row=0)

        # Detailed instructions shown to the user, including the current exchange rate
        # The exchange rate is pulled from the NZD_TO_VND constant so it stays accurate
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

        # Dismiss button closes the help window and re-enables the help button
        self.dismiss_button = Button(self.help_frame,
                                     font=("Arial", "12", "bold"),
                                     text="Dismiss", bg="#CC6600", fg="#FFFFFF",
                                     command=partial(self.close_help, partner))
        self.dismiss_button.grid(row=2, padx=10, pady=10)

        # Apply the orange background colour to all widgets in the help frame
        for widget in [self.help_frame, self.help_heading, self.help_text]:
            widget.config(bg=background)

    def close_help(self, partner):
        """Re-enables the help button on the main window and destroys this popup.

        Args:
            partner: The Converter instance, used to re-enable its help button.
        """
        partner.to_help_button.config(state=NORMAL)
        self.help_box.destroy()


class HistoryExport:
    """Creates a popup window showing the user's conversion history.

    Displays up to MAX_CALCS recent calculations (newest first).
    If there are more than MAX_CALCS calculations, a warning background
    is shown to indicate not all results are displayed.
    Includes an Export button that saves all calculations to a .txt file.
    """

    def __init__(self, partner, calculations):
        """Sets up the history window layout, displays calculations, and
        provides export functionality.

        Args:
            partner: The Converter instance that opened this window.
                     Used to re-enable the history button on close.
            calculations (list): The full list of conversion result strings
                                 from the main Converter instance.
        """
        self.history_box = Toplevel()
        self.history_box.title("History / Export")

        # Disable the history button on the main window to prevent duplicate popups
        partner.to_history_button.config(state=DISABLED)

        # Bind the X button to close_history to ensure the button is re-enabled
        self.history_box.protocol("WM_DELETE_WINDOW",
                                  partial(self.close_history, partner))

        # Frame to contain all history window widgets
        self.history_frame = Frame(self.history_box)
        self.history_frame.grid()

        # Change background colour and intro text depending on whether all
        # calculations fit within the MAX_CALCS display limit
        if len(calculations) <= MAX_CALCS:
            calc_back = "#D5E804"   # Yellow-green: all calculations shown
            calc_amount = "all your"
        else:
            calc_back = "#ffe6cc"   # Orange warning: only recent results shown
            calc_amount = (f"your recent calculations - "
                           f"showing {MAX_CALCS} / {len(calculations)}")

        recent_intro_txt = f"Below are {calc_amount} calculations."

        # Reverse the list so the most recent conversion appears at the top
        newest_first = list(reversed(calculations))

        # Slice to only show up to MAX_CALCS results in the display
        display_list = newest_first[:MAX_CALCS]

        # Join the display list into a single newline-separated string for the label
        newest_first_string = "\n".join(display_list)

        export_instruction_txt = ("Press <Export> to save your calculations to a "
                                  "text file. If the file already exists, it will "
                                  "be overwritten.")

        # List of label configurations: [text, font, background colour]
        # Using a list avoids repetitive Label() calls
        history_labels_list = [
            ["History / Export", ("Arial", "16", "bold"), None],
            [recent_intro_txt, ("Arial", "11"), None],
            [newest_first_string, ("Arial", "14"), calc_back],
            [export_instruction_txt, ("Arial", "11"), None]
        ]

        # Create each label from the list and add to the history window
        history_label_ref = []
        for count, item in enumerate(history_labels_list):
            lbl = Label(self.history_box,
                        text=item[0], font=item[1], bg=item[2],
                        wraplength=300, justify="left", pady=10, padx=20)
            lbl.grid(row=count)
            history_label_ref.append(lbl)

        # Store reference to the export instruction label so it can be
        # updated with a success message after exporting
        self.export_filename_label = history_label_ref[3]

        # Frame for the Export and Close buttons at the bottom of the window
        self.hist_button_frame = Frame(self.history_box)
        self.hist_button_frame.grid(row=4)

        # Button configuration: [label, colour, command, row, column]
        button_details_list = [
            ["Export", "#004C99",
             lambda: self.export_data(calculations), 0, 0],
            ["Close", "#666666",
             partial(self.close_history, partner), 0, 1],
        ]

        # Create each button from the list above
        for btn in button_details_list:
            Button(self.hist_button_frame,
                   font=("Arial", "12", "bold"),
                   text=btn[0], bg=btn[1], fg="#FFFFFF", width=12,
                   command=btn[2]).grid(row=btn[3], column=btn[4],
                                        padx=10, pady=10)

    def export_data(self, calculations):
        """Saves all conversion history to a dated .txt file.

        The filename includes today's date in YYYY_MM_DD format so that
        each day's exports have a unique name. The file is written with
        a header, the exchange rate used, and all calculations oldest-first.
        If a file with the same name exists, it will be overwritten.

        Args:
            calculations (list): The full list of conversion result strings.
        """
        # Get today's date components for the filename
        today = date.today()
        day = today.strftime("%d")
        month = today.strftime("%m")
        year = today.strftime("%Y")

        # Build filename using date to make each export uniquely identifiable
        file_name = f"currency_conversions_{year}_{month}_{day}"
        write_to = f"{file_name}.txt"

        # Write all calculations to the file (oldest to newest order)
        with open(write_to, "w") as text_file:
            text_file.write("***** Currency Conversions (NZD <-> VND) ******\n")
            text_file.write(f"Generated: {day}/{month}/{year}\n")
            # Use the NZD_TO_VND constant so the rate in the file always matches
            # what was actually used during the session
            text_file.write(f"Exchange rate used: 1 NZD = {NZD_TO_VND:,} VND\n\n")
            text_file.write("Calculation history (oldest to newest):\n")
            for item in calculations:
                text_file.write(item + "\n")

        # Update the export instruction label to confirm the file was saved
        success_string = (f"Export successful! File saved as {file_name}.txt")
        self.export_filename_label.config(
            fg="#009900", text=success_string,
            font=("Arial", "12", "bold"))

    def close_history(self, partner):
        """Re-enables the history button on the main window and destroys this popup.

        Args:
            partner: The Converter instance, used to re-enable its history button.
        """
        partner.to_history_button.config(state=NORMAL)
        self.history_box.destroy()


# --- Main Program Entry Point ---
# Only runs when this file is executed directly, not when imported as a module
if __name__ == "__main__":
    root = Tk()
    root.title("NZD ↔ VND Currency Converter")
    # Create an instance of the Converter class to build and display the main window
    Converter()
    # Start the tkinter event loop to keep the window open and responsive
    root.mainloop()
