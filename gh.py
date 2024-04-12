'''
OPS445 Assignment 2
Program: duim.py 
Author: "Simran Kaur"
The python code in this file (duim.py) is original work written by
"Simran Kaur". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This Script is an improved version of the 'du' tool for inspecting directories. 
It calls the 'du' command with max depth 1 on a specified directory and generates a bar graph 
representation of the drive space usage for each subdirectory within the specified directory.

Date: 4/12/2024 
'''

#!/usr/bin/env python3

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
    # Parse command-line arguments
    args = parse_command_args()
    # Check if the specified target is a valid directory
    if not os.path.isdir(args.target):
        print("Error: Invalid directory specified.")
        sys.exit(1)

    # Call call_du_sub() with the specified target directory to get subdirectories and their sizes
    subdirectories = call_du_sub(args.target)
    # Create a dictionary mapping directories to their sizes
    dir_dict = create_dir_dict(subdirectories)

    # Total size of the target directory
    total_size = sum(dir_dict.values())

    # Print headers for the output table with appropriate formatting and colors
    print(f"{'Percentage':<6} {'Graph':<21} {Fore.BLUE}{'Size':<11} {Style.RESET_ALL}{'Subdirectory'}")
    # Print a separator line
    print("-" * 55)

    # Sort directories by percentage size in descending order
    sorted_dirs = sorted(dir_dict.items(), key=lambda x: x[1], reverse=True)

    # Iterate through sorted directories and print information for each
    for directory, size in sorted_dirs:
        # Calculate percentage of directory size compared to total size
        percent = (size / total_size) * 100
        # Generate a bar graph representing the percentage
        graph = percent_to_graph(percent, 20)
        # Convert directory size to human-readable format if requested
        size_str = bytes_to_human_r(size) if args.human_readable else f"{size} bytes"
        # Print directory information with appropriate formatting and colors
        print(f"{Fore.GREEN}{percent:.2f}%{Style.RESET_ALL}  [{graph}] {Fore.BLUE}{size_str:<11} {Style.RESET_ALL}{directory}")

    # Print a separator line
    print("-" * 60)
    # Convert total size to human-readable format if requested
    total_size_str = bytes_to_human_r(total_size) if args.human_readable else f"{total_size} bytes"
    # Print total size and target directory
    print(f"Total: {total_size_str} {args.target}")

if __name__ == "__main__":
    main()
