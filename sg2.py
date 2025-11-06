#Language: Python 3
#IDE used: Thonny, GitHub Web IDE, and VS code
#Team: Robert Ford, Joel Jefferson, Elisa Reyes, Hannah Smid
#Project Info: Class: 4500 | Project: SG2| Date: 11/02/2025
#Purpose: The purpose of this project is to build off 
#the previous SG1 project and add cordance and 3 extra lists.
#Resources: W3School.com | realpython.com | learnpython.com


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
    
# Open File Logic

def openFile(words):
    txtfile = "CONCORDANCE.txt"
    content = sorted(words)
    try:
        with open(txtfile, 'w', encoding='utf-8') as file:
            for item in content:
                file.write(f"{item}\n")
            print(f"File '{txtfile}' created and written to successfully.")
    except IOError as e:
        print(f"Error writing to file '{txtfile}': {e}")
        

#This will return the first word on line for split words
def _first_word_on_line(line: str):
   word = ""
   started = False
   for ch in line.strip():
       if ch.isalpha() or ch == "-":
           word += ch
           started = True
       elif started:
           break
   return word.lower() if word else None

#This will take the test files and make inti lowercase words per line.
#This also combines the hyphenated word into a singular word
#Howevre it keeps internal hiphens and returns a list
def split_file_into_lines(file_name):
   with open(file_name, "r", encoding="utf-8") as file:
       text = file.read()
   text = combine_hyphens(text)
   lines = text.splitlines()


   words_by_line = []
   skip_next_word = False 


   for i, line_text in enumerate(lines):
       words_here = [w.lower() for w in _word_pattern.findall(line_text)]


       if skip_next_word and words_here:
           words_here = words_here[1:]
           skip_next_word = False


       if line_text.rstrip().endswith("-") and i + 1 < len(lines):
           next_line = lines[i + 1]
           next_words = [w.lower() for w in _word_pattern.findall(next_line)]


           if next_words:
               base_part = re.sub(r"[^A-Za-z]", "", line_text.split()[-1][:-1]).lower()
               merged_word = base_part + next_words[0]
               if words_here:
                   words_here[-1] = merged_word
               else:
                   words_here.append(merged_word)
               skip_next_word = True


       words_by_line.append(words_here)


   return words_by_line


# help enforce the hyphen to be considered as appearing before the letter a in SG2 reuiremnts
def sort_key_for_word(word):
   adjusted = word.lower().replace("-", "\x00")
   return tuple(adjusted)


#This variable it to build the concordance it will be able to return
#Condance which will consit of one long list that will contain all the 
#words in all the user indicated files
def build_concordance(file_list):
    concordance = {}
    files_word_sets = []

    for file_index, filename in enumerate(file_list, start=1):
        line_words = split_file_into_lines(filename)
        file_unique_words = set()

        for line_number, words_on_line in enumerate(line_words, start=1):
            for word_number, word in enumerate(words_on_line, start=1):
                file_unique_words.add(word)
                if word not in concordance:
                    concordance[word] = []
                concordance[word].append((file_index, line_number, word_number))

        files_word_sets.append(file_unique_words)

    for word, positions in concordance.items():
        positions.sort()

    return concordance, files_word_sets


#This will print the concordance and transfer the text to the
#CONCORDANCE.TXT file
#Used this site as a resource: https://realpython.com/python-sort
#Used this site as a resource: https://learnpython.com/blog/python-custom-sort-function
def print_and_write_concordance(concordance):
    sorted_words = sorted(concordance.keys(), key=sort_key_for_word)
    out_lines = []

    for word in sorted_words:
        positions = []
        for (file_num, line_num, word_num) in concordance[word]:
            positions.append(f"{file_num}.{line_num}.{word_num}")
        formatted_positions = "; ".join(positions) + "."
        out_lines.append(f"{word} {formatted_positions}")

    print("\nConcordance (also written to CONCORDANCE.TXT):")
    for entry in out_lines:
        print(entry)

    with open("CONCORDANCE.TXT", "w", encoding="utf-8") as f:
        for entry in out_lines:
            f.write(entry + "\n")


#This will be to format the table accoridng to the SG2 specifications
#Used this site as a resource: https://learnpython.com/blog/python-custom-sort-function
def align_table(rows, headers=None):
    str_rows = [[str(c) for c in row] for row in rows]
    if headers:
        str_rows.insert(0, headers)

    num_cols = len(str_rows[0]) if str_rows else 0
    widths = [0] * num_cols
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    fmt = " ".join(f"{{:>{w}}}" for w in widths)

    out = []
    if headers:
        out.append(fmt.format(*headers))
        out.append("-" * (sum(widths) + (len(widths) - 1)))
        data_rows = str_rows[1:]
    else:
        data_rows = str_rows

    for row in data_rows:
        out.append(fmt.format(*row))
    return out


# Main Program Logic

def main():
    intro = ( #updated the intro for the SG2
        "SG2: Word count, Search, Cordance, and Extra Lists\n"
        "This program reads up to 10 text files (.TXT), parses words (letters and optional internal hyphens),\n"
        "reports per-file totals and distinct counts, and lets you search words across the files (case-insensitive).\n"
        "This program also adds a CORDANCE.TXT and ExtraLists.txt with three formated list"
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

        openFile(words) #stores words in alphabetival order
        
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
