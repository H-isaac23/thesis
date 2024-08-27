from pathlib import Path
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from rouge_score.score.types import rouge_n
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
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
        textrank_summarizer = TextRankSummarizer()
        summary = textrank_summarizer(parser.document, 10)  # Summarize the document to 10 sentences
        pdf_textrank_summary = ""
        # Output the summary
        for sentence in summary:
            pdf_textrank_summary += str(sentence)
        scorer = rouge_scorer.RougeScorer(rouge_n, use_stemmer=True)
        scores = scorer.score(pdf_text, pdf_textrank_summary)
        temp = "\nTextRank: "
        for v in scores.values():
            temp += f"Precision: {v.precision}, Recall: {v.recall}"
        scores_text += temp


        '''
        Luhn
        '''
        # Create a Luhn summarizer
        luhn_summarizer = LuhnSummarizer()
        pdf_luhn_summary = ""
        # Summarize the text with a specified number of sentences
        for sentence in luhn_summarizer(parser.document, 20):  # Summarize to 5 sentences
            pdf_luhn_summary += str(sentence)
        scorer = rouge_scorer.RougeScorer(rouge_n, use_stemmer=False)
        scores = scorer.score(pdf_text, pdf_luhn_summary)
        temp = "\nLuhn: "
        for v in scores.values():
            temp += f"Precision: {v.precision}, Recall: {v.recall}"
        scores_text += temp

        '''
        LexRank
        '''
        # Create a LexRank summarizer
        lex_summarizer = LexRankSummarizer()
        pdf_lex_summary = ""
        # Summarize the text with a specified number of sentences
        for sentence in lex_summarizer(parser.document, 20):  # Summarize to 5 sentences
            pdf_lex_summary += str(sentence)
        scorer = rouge_scorer.RougeScorer(rouge_n, use_stemmer=False)
        scores = scorer.score(pdf_text, pdf_lex_summary)
        temp = "\nLex: "
        for v in scores.values():
            temp += f"Precision: {v.precision}, Recall: {v.recall}"
        scores_text += temp

        '''
        LSA
        '''
        # Create a LSA summarizer
        lsa_summarizer = LsaSummarizer()
        pdf_lsa_summary = ""
        # Summarize the text with a specified number of sentences
        for sentence in lsa_summarizer(parser.document, 20):  # Summarize to 5 sentences
            pdf_lsa_summary += str(sentence)
        scorer = rouge_scorer.RougeScorer(rouge_n, use_stemmer=False)
        scores = scorer.score(pdf_text, pdf_lsa_summary)
        temp = "\nLsa: "
        for v in scores.values():
            temp += f"Precision: {v.precision}, Recall: {v.recall}"
        scores_text += temp

        scores_text += "\n" + "-" * 200 + "\n"

    if directory[-1] == "s":
        suffix = "1"
    else:
        suffix = directory[-1]
    with open(f'thesis3_scores/r5_scores{suffix}.txt', 'w') as file:
        try:
            file.write(scores_text)
        except:
            print("WHYYYYYYYYYYYYYYYYYY")


traverse_directory_pathlib("./pdfs")
traverse_directory_pathlib("./pdfs2")
traverse_directory_pathlib("./pdfs3")

