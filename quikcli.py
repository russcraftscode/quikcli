#!/usr/bin/env python3
# Filename: quikcli.py
# Author: Russell Johnson
# Created: November 22, 2025
# Version: 2.0
"""Quikcli – a tiny console‑prompting helper.

This module handles prompting the user for responses and ensuring those responses are properly formatted.
Pronounced "quickly".
"""
import os
import enum

# ------------
# Constants
# ------------

# Default visual layout parameters
DEFAULT_SCREEN_WIDTH: int = 80  # default width of the prompt box (columns)
DEFAULT_MAX_LINES: int = 30  # max number of rows before a paging is required TODO
DEFAULT_H_BORDER: str = '-'  # character used for top/bottom borders
DEFAULT_V_BORDER: str = '|'  # character used for left/right borders


class Input_Formats(enum.Enum):
    """Supported input validation modes for :meth:`QuikCLI.prompt_user`.

    YN: Accepts only 'yes' or 'no'. Returns True / False

    INTEGER: Accepts a string consisting only of decimal digits. Returns int

    NUMERIC: TODO
    """
    YN = 1
    INTEGER = 2
    NUMERIC = 3

# ------------
# Static Functions
# ------------

def clear_screen(warn=True):
    """
    Clears the console output. Should work on win and mac/unix/linx
    :param warn: print a message to the user if the screen failed to clear. Default true
    """

    if warn:  # If the screen clears the user will not see this
        print("Note: Attempting to clear screen. Please use a standard terminal emulator.")
    # Windows systems
    if os.name == 'nt':
        _ = os.system('cls')
    # Unix-like systems such as Linux or macOS
    else:
        _ = os.system('clear')


def line_split(text: str, max_length: int) -> list[str]:
    """
    Splits text into max_length lines while trying not to cut words in half
    :param text: text to split
    :param max_length: max length of a line
    :return: list of lines of split text
    """
    lines = []
    remaining_text = text
    # Keep cutting text into lines until remaining text fits on one line
    while len(remaining_text) > max_length:
        split_point = max_length
        # Look for a space to split the line
        while not remaining_text[split_point].isspace():
            split_point -= 1
            # If no space found split then just split a word
            if split_point == 0:
                split_point = max_length
                break
        # Create new line with text up to split point
        lines.append(remaining_text[:split_point])
        # Remove used text
        remaining_text = remaining_text[split_point:]
    # Make a final line with any remaining text
    lines.append(remaining_text)
    return lines


class Quikcli:
    def __init__(self,
                 max_width: int = DEFAULT_SCREEN_WIDTH,
                 max_lines: int = DEFAULT_MAX_LINES,
                 v_border: str = DEFAULT_V_BORDER,
                 h_border: str = DEFAULT_H_BORDER,
                 i_border: str = DEFAULT_H_BORDER,
                 default_required: bool = True,
                 app_header: str = None,
                 warn_screen_clear: bool = True,
                 ):
        """
        :param max_width: Max number of horizontal characters
        :param max_lines: Max number of lines before pg-up/pg-dn
        :param v_border: Character used on vertical "wall" borders of prompt box
        :param h_border: Character used on top and bottom borders of prompt box
        :param i_border: Character used to divide sections inside a prompt
        :param default_required: All questions require an answer unless specified. Default True
        :param app_header: Line displayed above the prompt box
        """
        self.v_border = v_border
        self.h_border = h_border
        self.i_border = i_border
        self.max_screen_width = max_width
        self.max_lines = max_lines
        self.default_required = default_required
        self.app_header = app_header
        self.warn_screen_clear = warn_screen_clear

        # TODO: implement 'n' 'b' for next, back paging when there is to much to fit on one page

    def _display_prompt(self, query, max_width, options=None, header=None):
        """
        Displays a question for the user
        :param query: Question to be asked
        :param max_width: Horizontal size limitation
        :param options: Optional list of choices
        :param header: Optional line above question
        """
        # TODO: add line tracking to prevent going over on vertical space
        lines_used = 3  # for top and bottom borders plus internal divider

        # create borders
        max_len = max_width - 4  # max size of content in a row
        top_bottom_border = self.h_border * max_width
        internal_divider = self.v_border + (self.i_border * (max_width - 2)) + self.v_border
        blank_row = self.v_border + (' ' * (max_width - 2)) + self.v_border

        print(top_bottom_border)
        # display the header if there is one
        if header:
            header_lines = line_split(header, max_len)
            for line in header_lines:
                print(f"{self.v_border} {line:<{max_len}} {self.v_border}")
                lines_used += 1
            print(blank_row)
            lines_used += 1
        # display the query
        question_lines = line_split(query, max_len)
        for line in question_lines:
            print(f"| {line:<{max_len}} |")
            lines_used += 1

        # Print the options if there are any
        if options:
            print(internal_divider)
            max_len -= 4  # Cut the length of the display by 4 to allow for option numbering
            for i, option in enumerate(options):
                chunks = [option[i:i + max_len] for i in range(0, len(option), max_len)]
                # print the 1st line of the option
                print(f"| {i + 1} - {chunks[0]:<{max_len}} |")
                lines_used += 1
                # print any additional lines
                for j in range(1, len(chunks)):
                    print(f"|     {chunks[j]:<{max_len}} |")
                    lines_used += 1
        print(top_bottom_border)

    def prompt_user(self,
                    query,
                    menu_options=None,
                    input_format=None,
                    input_length=None,
                    screen_width=None,
                    header=None,
                    required=None,
                    instructions=None):
        """
        Prompts the user for input. Chooses the appropriate display type for the question
        :param query: Question to ask the user
        :param menu_options: List of options that the user may pick from (optional)
        :param input_format: Optional constraint on user response ["y/n", "numeric", "int"]
        :param input_length: Optional constraint requiring user to respond with that many characters
        :param screen_width: Character width length of the display. Defaults to 80 chars
        :param header: optional line to display above the question
        :param required: is the user required to give an answer. Defaults to true
        :return: the response of the user. Type will be determined by 'format' parameter. Defaults to string
        """
        # TODO: add pg-up pg-dn for long displays
        error_message = None

        if required is None:  # If not specified, go with default
            response_required = self.default_required
        else:
            response_required = required

        while True:
            clear_screen(warn=self.warn_screen_clear)
            print(self.app_header)  # may be blank

            # show question
            self._display_prompt(query,
                                 options=menu_options,
                                 max_width=self.max_screen_width if screen_width is None else screen_width,
                                 header=header,
                                 )

            # If the user has previously entered mis-formed response, show the error message
            if error_message:
                print(error_message)

            # Get user response
            if instructions:  # if instructions are specified
                response = input(instructions)

            elif menu_options:
                if response_required:
                    response = input("Enter your selection number: ")
                else:
                    response = input("Enter your selection number [enter nothing to skip]: ")

            elif input_format == Input_Formats.YN:
                if response_required:
                    response = input("Enter <yes/no>: ")
                else:
                    response = input("Enter <yes/no/leave blank>: ")

            elif input_format == Input_Formats.INTEGER:  # Enforce 0-9 only
                if response_required:
                    response = input("Enter digits only, no commas or symbols: ")
                else:
                    response = input("Enter digits only, no commas or symbols [enter nothing to skip]: ")

            else:  # Free form response
                if response_required:
                    response = input(": ")
                else:
                    response = input("[enter nothing to skip]: ")

            # Strip any trailing or leading whitespace from response
            response = response.strip()

            # Validate response
            if input_format == Input_Formats.YN:
                if len(response) > 0:  # Some answer was given
                    if response[0].lower() == 'y': return True
                    if response[0].lower() == 'n': return False
                    error_message = "Invalid Input: Response must start with 'y' or 'n'"
                elif response_required:  # no answer given and answer is required
                    error_message = "Invalid Input: Question cannot be skipped"
                else:  # no answer given and not required
                    return None

            elif input_format == Input_Formats.INTEGER:
                if len(response) > 0:  # Some answer was given
                    if response.isdecimal():
                        return int(response)
                    else:
                        error_message = "Invalid Input: Response must contain only digits 0-9"
                elif response_required:  # No answer given and answer IS required
                    error_message = "Invalid Input: Question cannot be skipped"
                else:  # No answer given and NOT required
                    return None

            else:  # Free form response
                if response_required and len(response) == 0:
                    error_message = "Invalid Input: Question cannot be skipped"
                else:
                    return response


def main():
    """
    This function is just used for dev demoing
    """
    print("Running in dev mode")

    test_app_header = " *** Running in dev mode ***"

    test_prompter = Quikcli(app_header=test_app_header, warn_screen_clear=False)

    test_header1 = "This is question 1"
    test_header2 = "This is question 2"
    test_header3 = "This is question 3"
    test_header4 = "This is question 4"
    test_question = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut" +
                     " labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco" +
                     " laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in " +
                     "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat" +
                     " non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")

    test_options = ["alpha", "beta", "gamma"]

    line_split("abc", 2)

    test_prompter.prompt_user(test_question, menu_options=test_options, header=test_header1)
    test_prompter.prompt_user(test_question, header=test_header2)
    test_prompter.prompt_user(test_question, input_format=Input_Formats.YN, header=test_header3)
    test_prompter.prompt_user(test_question, input_format=Input_Formats.INTEGER, header=test_header4)


if __name__ == "__main__":
    main()
