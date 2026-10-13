import csv
import os

def print_table(filename="stochastic.csv"):
    """Reads a CSV file and prints a nicely formatted table to the terminal."""
    if not os.path.exists(filename):
        print(f"File '{filename}' not found!")
        return

    with open(filename, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        
    if not reader:
        print(f"File '{filename}' is empty.")
        return

    header = reader[0]
    rows = reader[1:]

    if not rows:
        print("No data rows found in the file.")
        return

    # Calculate maximum width for each column to align the text properly
    col_widths = [len(col) for col in header]
    for row in rows:
        for i, val in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(val))

    # Helper function to print a horizontal separator line
    def print_separator():
        sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
        print(sep)

    # Helper function to print a table row
    def print_row(row_data):
        formatted = " | ".join(val.ljust(col_widths[i]) for i, val in enumerate(row_data))
        print(f"| {formatted} |")

    print(f"\n--- Results from {filename} ---")
    
    # Draw the table
    print_separator()
    print_row(header)
    print_separator()
    
    for row in rows:
        print_row(row)
        
    print_separator()
    print()

if __name__ == "__main__":
    print_table("stochastic.csv")