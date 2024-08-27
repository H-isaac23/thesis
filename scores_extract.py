import pandas as pd
import re

# Reading the file
# f1 = './thesis3_scores/scores1.txt'
# f1_out = './thesis3_scores/extracted_scores_1.xlsx'
#
# f2 = './thesis3_scores/scores2.txt'
# f2_out = './thesis3_scores/extracted_scores_2.xlsx'
#
# f3 = './thesis3_scores/scores3.txt'
# f3_out = './thesis3_scores/extracted_scores_3.xlsx'

l1 = './thesis3_scores/r5_scores1.txt'
l1_out = './thesis3_scores/extracted_scores_1.xlsx'

l2 = './thesis3_scores/r5_scores2.txt'
l2_out = './thesis3_scores/extracted_scores_2.xlsx'

l3 = './thesis3_scores/r5_scores3.txt'
l3_out = './thesis3_scores/extracted_scores_3.xlsx'



def extract_scores(filename, output_filename):
    with open(filename, 'r', encoding='ISO-8859-1') as file:
        file_contents = file.read()

    # Splitting the content by lines
    lines = file_contents.split('\n')

    # Regex pattern to match the scores
    pattern = r"precision=([\d\.]+), recall=([\d\.]+)"

    # Lists for titles, precisions, and recalls
    titles = []
    precisions = []
    recalls = []

    # Extracting titles and scores
    for i in range(0, len(lines), 3):  # Increment by 3 to skip the separator lines
        if i+1 < len(lines):  # Ensure there is a line for the score
            title = lines[i]
            score_line = lines[i+1]

            # Extract precision and recall using regex
            match = re.search(pattern, score_line)
            if match:
                titles.append(title)
                precisions.append(float(match.group(1)))
                recalls.append(float(match.group(2)))

    # Creating the DataFrame
    corrected_df = pd.DataFrame({
        'Title': titles,
        'Precision Score': precisions,
        'Recall Score': recalls
    })

    # Saving to an Excel file
    corrected_df.to_excel(output_filename, index=False)


def extract_lscores(filename, output_filename):
    # File path of the uploaded text file

    # Reading the file with a different encoding if UTF-8 doesn't work
    with open(filename, 'r', encoding='ISO-8859-1') as file:
        file_content = file.readlines()

    # Initializing variables
    title = None
    precision_tr = recall_tr = precision_luhn = recall_luhn = precision_lex = recall_lex = precision_lsa = recall_lsa = None

    # List to hold the parsed data
    data = []

    # Parsing the file and extracting the required data
    for line in file_content:
        if line.startswith('pdfs\\') or line.startswith('pdfs2\\') or line.startswith('pdfs3\\'):  # Filename line
            # Process the previous record if title is not None
            if title is not None:
                data.append([title, precision_tr, recall_tr, precision_luhn, recall_luhn, precision_lex, recall_lex, precision_lsa, recall_lsa])
            # Extracting new title
            title = line.split('\\')[-1].strip()
        elif line.startswith('TextRank:'):
            # Extracting TextRank precision and recall
            parts = line.split(',')
            precision_tr = float(parts[0].split(':')[-1])
            recall_tr = float(parts[1].split(':')[-1])
        elif line.startswith('Luhn:'):
            # Extracting Luhn precision and recall
            parts = line.split(',')
            precision_luhn = float(parts[0].split(':')[-1])
            recall_luhn = float(parts[1].split(':')[-1])
        elif line.startswith('Lex:'):
            # Extracting TextRank precision and recall
            parts = line.split(',')
            precision_lex = float(parts[0].split(':')[-1])
            recall_lex = float(parts[1].split(':')[-1])
        elif line.startswith('Lsa:'):
            # Extracting Luhn precision and recall
            parts = line.split(',')
            precision_lsa = float(parts[0].split(':')[-1])
            recall_lsa = float(parts[1].split(':')[-1])

    # Adding the last record
    if title is not None:
        data.append([title, precision_tr, recall_tr, precision_luhn, recall_luhn, precision_lex, recall_lex, precision_lsa, recall_lsa])

    # Creating a DataFrame
    columns = ['Title', 'Precision (TextRank)', 'Recall (TextRank)', 'Precision (Luhn)', 'Recall (Luhn)', 'Precision (Lex)', 'Recall (Lex)', 'Precision (Lsa)', 'Recall (Lsa)']
    df = pd.DataFrame(data, columns=columns)

    # Writing the DataFrame to an Excel file
    df.to_excel(output_filename, index=False)


# extract_scores(f1, f1_out)
# extract_scores(f2, f2_out)
# extract_scores(f3, f3_out)
extract_lscores(l1, l1_out)
extract_lscores(l2, l2_out)
extract_lscores(l3, l3_out)
