# Using PyPDF2
import PyPDF2
from rouge_score import rouge_scorer
from rouge_score.scores.types import rouge_n
from pathlib import Path


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text

def extract_text_from_summary(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    return text

def traverse_directory_pathlib(directory, summary_dir):
    path = Path(directory)
    files = list(path.rglob("*"))
    num_pdfs = len(files)
    scores_text = ""

    for x in range(num_pdfs):
        # file_path = str(files[x])
        filename = str(files[x]).split("\\")[1].split(".pdf")[0]
        print(filename)
        pdf_text = extract_text_from_pdf(f'{directory}/{filename}.pdf')
        pdf_summary = extract_text_from_summary(f'{summary_dir}/{filename}.txt')

        # print(pdf_text)
        # print(pdf_summary)

        scorer = rouge_scorer.RougeScorer(rouge_n, use_stemmer=True)
        scores = scorer.score(pdf_text, pdf_summary)

        scores_text += filename + "\n"
        temp = ""
        for v in scores.values():
            temp += f"Precision: {v.precision}, Recall: {v.recall}"
        scores_text += temp
        scores_text += "\n" + "-"*200 + "\n"

    with open(f'scores2.txt', 'w') as file:
        try:
            print("hi")
            file.write(scores_text)
        except:
            print("Why")


traverse_directory_pathlib("./pdfs2", "./ps2")

