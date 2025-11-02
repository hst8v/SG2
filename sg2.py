import re
import os
import sys

# Helper / Core Functions

def is_txt_filename(fname: str) -> bool:
    #Return True if fname ends with .txt (case-insensitive).
    return fname.lower().endswith('.txt')

def prompt_input(prompt: str) -> str:
    #Wrapper for input to make testing easier (and consistent prompts).
    try:
        return input(prompt)
    except EOFError:
        # graceful exit if input stream closed
        print("\nInput closed. Exiting.")
        sys.exit(0)

def prompt_yes_no(prompt: str) -> bool:
    """
    Prompt for a Yes/No answer. Accepts: yes, no, y, n (any case).
    Returns True for Yes, False for No.
    Continues prompting until a valid response given.
    """
    valid_yes = {'yes', 'y'}
    valid_no = {'no', 'n'}
    while True:
        ans = prompt_input(prompt).strip().lower()
        if ans in valid_yes:
            return True
        if ans in valid_no:
            return False
        print("Invalid response. Please answer 'Yes' or 'No' (y/n).")

# regex: letters with optional internal hyphens (one or more groups separated by hyphens)
WORD_RE = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*")

def normalize_word(word: str) -> str:
    #Normalize a word for case-insensitive comparison (lowercase).
    return word.lower()

def parse_text_handling_line_hyphens(lines):
    """
    Given list of lines from a file, return a single string where lines that end with a hyphen
    WITHOUT a space before the hyphen are joined to the next line (the hyphen removed).
    Otherwise, newlines replaced with spaces.
    """
    processed_parts = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        # Check if the line ends with '-' AND the character before hyphen is not a space,
        # i.e., "...hyphenated-" but NOT " ... -"
        if line.endswith('-') and (len(line) >= 2 and line[-2] != ' '):
            # Remove the trailing hyphen
            left = line[:-1]
            # If there is a next line, consume and join starting from its leading characters
            if i + 1 < len(lines):
                next_line = lines[i+1].lstrip()  # remove leading whitespace from next line
                joined = left + next_line
                # Now, treat joined as a single new "line" and skip the next line (we consumed it)
                processed_parts.append(joined)
                i += 2
                continue
            else:
                # last line ends with hyphen; remove hyphen and continue
                processed_parts.append(left)
                i += 1
                continue
        else:
            # normal line break; replace with a space to not join words across lines
            processed_parts.append(line)
            i += 1
    # join with spaces to preserve separation between processed parts
    return ' '.join(processed_parts)

def extract_words_from_text(text: str):
    """
    Extract words according to LEGAL word definition:
    - series of alphabetic characters
    - internal hyphen(s) allowed between alphabetic groups (e.g., 'first-base', 'well-known')
    Returns a list of words in the order found.
    """
    return WORD_RE.findall(text)

# Printing / Formatting

def print_file_summary(file_order, word_data):
    """
    Print a formatted table with columns:
      Filename | Total words | Distinct words
    Right-justified columns, preserve file_order list.
    """
    # Compute values
    rows = []
    for fname in file_order:
        words = word_data[fname]
        total = len(words)
        distinct = len(set(normalize_word(w) for w in words))
        rows.append((fname, total, distinct))
    # Determine column widths
    max_fname_len = max((len(r[0]) for r in rows), default=8)
    max_total_len = max((len(str(r[1])) for r in rows), default=5)
    max_dist_len = max((len(str(r[2])) for r in rows), default=7)
    # Print header
    header_fname = "Filename"
    header_total = "TotalWords"
    header_dist = "DistinctWords"
    print()
    print(f"{header_fname:>{max_fname_len}}  {header_total:>{max_total_len}}  {header_dist:>{max_dist_len}}")
    print('-' * (max_fname_len + max_total_len + max_dist_len + 4))
    # Print rows
    for fname, total, distinct in rows:
        print(f"{fname:>{max_fname_len}}  {str(total):>{max_total_len}}  {str(distinct):>{max_dist_len}}")
    print()

def print_search_results_for_word(word, results):
    #results is dict filename -> count
    
    print()
    print(f"Results for word '{word}':")
    for fname, cnt in results.items():
        print(f"  {fname}: {cnt}")
    print()

def print_search_history_summary(search_history, file_order):
    #search_history: list of tuples (legal_word, {filename: count})
    #Prints a table: rows = words, columns = filenames

    if not search_history:
        print("No searched words to summarize.")
        return
    # Prepare header
    words = [entry[0] for entry in search_history]
    # Column widths
    max_word_len = max(len("Word"), max((len(w) for w in words), default=4))
    fname_widths = {f: max(len(f), 5) for f in file_order}
    # header
    header_parts = [f"{'Word':<{max_word_len}}"]
    for f in file_order:
        header_parts.append(f"{f:>{fname_widths[f]}}")
    header_line = "  ".join(header_parts)
    print()
    print("Summary of searched words across files:")
    print(header_line)
    print('-' * len(header_line))
    # rows
    for word, counts in search_history:
        row_parts = [f"{word:<{max_word_len}}"]
        for f in file_order:
            row_parts.append(f"{str(counts.get(f,0)):>{fname_widths[f]}}")
        print("  ".join(row_parts))
    print()

# Main Program Logic

def main():
    intro = (
        "SG1: Word-count & Search Tool\n"
        "This program reads up to 10 text files (.TXT), parses words (letters and optional internal hyphens),\n"
        "reports per-file totals and distinct counts, and lets you search words across the files (case-insensitive).\n"
    )
    print(intro)
    # Containers
    file_list = []
    word_data = {}  # filename -> list of words (original order)
    MAX_FILES = 10

    #  File input loop 
    while len(file_list) < MAX_FILES:
        raw_fname = prompt_input("Enter a .TXT filename (in same directory as this script): ").strip()
        if not is_txt_filename(raw_fname):
            print("Filename must end with .TXT (case-insensitive). Please try again.")
            continue
        # Check duplicate
        if raw_fname in file_list:
            print("You already entered that filename. Enter a different filename or say No to add more files.")
            add_more = prompt_yes_no("Add another file? (Yes/No): ")
            if add_more:
                continue
            else:
                break
        # Check existence
        if not os.path.isfile(raw_fname):
            print(f"File '{raw_fname}' not found in current directory ({os.getcwd()}). Please try again.")
            continue
        # Try opening and parsing
        try:
            with open(raw_fname, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error opening file '{raw_fname}': {e}")
            continue

        # Preprocess lines to handle line-break hyphen rules
        combined_text = parse_text_handling_line_hyphens(lines)
        # Extract words
        words = extract_words_from_text(combined_text)
        # Store
        word_data[raw_fname] = words
        file_list.append(raw_fname)
        print(f"Loaded '{raw_fname}' with {len(words)} words ({len(set(normalize_word(w) for w in words))} distinct).")

        # If reached max files, stop asking
        if len(file_list) >= MAX_FILES:
            print(f"Reached maximum of {MAX_FILES} files.")
            break

        # Ask whether to add another file
        add_more = prompt_yes_no("Add another file? (Yes/No): ")
        if not add_more:
            break

    if not file_list:
        print("No files were entered. Program will exit.")
        return

    #  Print file summary 
    print_file_summary(file_list, word_data)

    #  Word search loop 
    search_history = []
    while True:
        # Prompt for LegalWord
        # LegalCharacters = 'abcdefghijklmnopqrstuvwxyz-'
        while True:
            candidate = prompt_input("Enter a word to search (letters and hyphen allowed): ").strip()
            if candidate == "":
                print("Empty input not allowed; please enter a legal word.")
                continue
            # Validate: must match pattern ^[A-Za-z]+(?:-[A-Za-z]+)*$
            if WORD_RE.fullmatch(candidate):
                legal_word = candidate
                break
            else:
                # find first problematic character/index for helpful message
                print("Invalid word. A legal word contains only letters and internal hyphen(s) (e.g., 'first-base').")
                print("Please try again.")

        # Count occurrences in each file
        lw_norm = normalize_word(legal_word)
        results = {}
        for fname in file_list:
            words = word_data[fname]
            cnt = sum(1 for w in words if normalize_word(w) == lw_norm)
            results[fname] = cnt

        # Display results
        print_search_results_for_word(legal_word, results)
        # Record in history
        search_history.append((legal_word, results))

        # Ask to continue searching
        again = prompt_yes_no("Search another word? (Yes/No): ")
        if not again:
            break

    # Final summary
    print_search_history_summary(search_history, file_list)

    # Finish
    prompt_input("Program finished. Press ENTER to exit.")
    print("Goodbye.")

if __name__ == "__main__":
    main()
