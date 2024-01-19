from pathlib import Path
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from rouge_score.score.types import rouge_n
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from rouge_score import rouge_scorer
import PyPDF2

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text

def traverse_directory_pathlib(directory):
    path = Path(directory)
    scores_text = ""
    for file in path.rglob('*'):
        print(file)
        scores_text += str(file)

        pdf_text = extract_text_from_pdf(f'.\\{file}')
        '''
        TEXTRANK
        '''

        # Parse the text
        parser = PlaintextParser.from_string(pdf_text, Tokenizer("english"))

        # Using TextRank summarizer
        summarizer = TextRankSummarizer()
        summary = summarizer(parser.document, 10)  # Summarize the document to 10 sentences
        pdf_summary = ""
        # Output the summary
        for sentence in summary:
            pdf_summary += str(sentence)
        scorer = rouge_scorer.RougeScorer(rouge_n, use_stemmer=True)
        scores = scorer.score(pdf_text, pdf_summary)
        temp = "\nTextRank: "
        for v in scores.values():
            temp += f"Precision: {v.precision}, Recall: {v.recall}"
        scores_text += temp + "\n"


        '''
        Luhn
        '''
        # Create a Luhn summarizer
        lsummarizer = LuhnSummarizer()
        pdf_lsummary = ""
        # Summarize the text with a specified number of sentences
        for sentence in lsummarizer(parser.document, 20):  # Summarize to 5 sentences
            pdf_lsummary += str(sentence)
        scorer = rouge_scorer.RougeScorer(rouge_n, use_stemmer=False)
        scores = scorer.score(pdf_text, pdf_lsummary)
        temp = "\nLuhn: "
        for v in scores.values():
            temp += f"Precision: {v.precision}, Recall: {v.recall}"
        scores_text += temp + "\n"

        scores_text += "\n" + "-"*200 + "\n"
    if directory[-1] == "s":
        suffix = "1"
    else:
        suffix = directory[-1]
    with open(f'r5_lscores{suffix}.txt', 'w') as file:
        try:
            file.write(scores_text)
        except:
            print("WHYYYYYYYYYYYYYYYYYY")


traverse_directory_pathlib("./pdfs")
# traverse_directory_pathlib("./pdfs2")
# traverse_directory_pathlib("./pdfs3")

