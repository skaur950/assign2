import os
import sys
import subprocess
import argparse
from colorama import Fore, Style

def parse_command_args():
    "Set up argparse here. Call this function inside main."
     # Initialize ArgumentParser object with description and epilog
    parser = argparse.ArgumentParser(description="DU Improved -- See Disk Usage Report with bar charts", epilog="Copyright 202X")
    # Add positional argument for target directory
    parser.add_argument("target", nargs='?', default=".", help="The directory to scan.")
    # Add optional argument for human-readable format
    parser.add_argument("-H", "--human-readable", action="store_true", help="Print sizes in human readable format (e.g. 1K 23M 2G)")
    # Add optional argument for specifying the length of the graph
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    # Parse the command-line arguments
    args = parser.parse_args()
    return args

def percent_to_graph(percent: int, total_chars: int) -> str:
    """
    Returns a string representing a bar graph of the given percentage.
    Args:
    percent (int): The percentage value (between 0 and 100).
    total_chars (int): The total number of characters in the bar graph.
    Returns:
    str: A string representing the bar graph.
    """
    # Check if percent is within the valid range
    if percent < 0 or percent > 100:
        print("Error: Percentage must be between 0 and 100")
        return None
    # Calculate the number of '#' symbols to print
    num_symbols = round(percent / 100 * total_chars)
    # Construct the bar graph string
    bar_graph = '#' * num_symbols + ' ' * (total_chars - num_symbols)
    return bar_graph

def call_du_sub(location: str) -> list:
    # Creating a command to run 'du -d 1' on the target directory
    command = ['du', '-d', '1', location]
    try:
        # Running the command and capturing the output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()  # Capturing the stdout (ignore stderr for now)
        # Decoding the output from bytes to a string using UTF-8 encoding
        output = output.decode('utf-8')
        # Extracting subdirectories from the output
        subdirectories = []  # Creating an empty list to store subdirectories
        for line in output.split('\n'):  # Looping through each line in the output
            if line.strip():  # Checking if the line is not empty
                parts = line.split()  # Split the line based on whitespace
                if len(parts) >= 2:
                    subdirectory = ' '.join(parts[1:])  # Combine the parts after the size as the subdirectory path
                    size = parts[0]  # The first part is assumed to be the size
                    subdirectories.append((subdirectory.strip(), int(size)))  # Adding the subdirectory to the list
                else:
                    print(f"Ignore line with insufficient parts: {line}")
        return subdirectories  # Returning the list of subdirectories
    except Exception as e:
        print(f"Error executing du command: {e}")  # Printing error message if command fails
        return []  # Returning an empty list in case of error

def create_dir_dict(raw_dat: list) -> dict:
    """
    Get list from call_du_sub, return dict {'directory': size} where size is in bytes.
    """
    # Initialize an empty dictionary to store directory sizes
    dir_dict = {}
    # Iterate over each tuple in the raw data list
    for item in raw_dat:
        try:
            subdirectory, size = item  # Unpack the tuple into subdirectory and size
            dir_dict[subdirectory.strip()] = size  # Add the subdirectory and size to the dictionary
        except ValueError:
            # Print a message indicating that the input is malformed
            print(f"Ignore malformed input: {item}")
    # Return the dictionary containing directory sizes
    return dir_dict

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 KiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

def main():
    args = parse_command_args()# parse command-line arguments
    if not os.path.isdir(args.target):  # Check if the specified target is a valid directory
        print("Error: Invalid directory specified.")
        sys.exit(1)

    subdirectories = call_du_sub(args.target)  # Call call_du_sub() with the specified target directory
    dir_dict = create_dir_dict(subdirectories)  # Create a dictionary mapping directories to their sizes

    total_size = sum(dir_dict.values())  # Total size of the target directory

    print(f"{'Subdirectory':<40} {'Percentage':<12} {'Size':<20} {'Graph'}")
    print("-" * 80)
    for directory, size in dir_dict.items():
        percent = (size / total_size) * 100  # Calculate percentage
        graph = percent_to_graph(percent, args.length)  # Generate bar graph
        size_str = bytes_to_human_r(size) if args.human_readable else str(size) + " bytes"
        # Colorize output based on percentage
        if percent >= 50:
            print(Fore.RED + f"{directory:<40} {percent:.2f}% {size_str:<20} [{graph}]" + Style.RESET_ALL)
        elif percent >= 20:
            print(Fore.YELLOW + f"{directory:<40} {percent:.2f}% {size_str:<20} [{graph}]" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"{directory:<40} {percent:.2f}% {size_str:<20} [{graph}]" + Style.RESET_ALL)

if __name__ == "__main__":
    main()

