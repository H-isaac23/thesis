import dotenv
from pathlib import Path
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate

dotenv.load_dotenv()

def summarize(file_path):
    # Define prompt
    prompt_template = """Write a concise summary for the introduction, process, results, and conclusion of the following (skip images), give back the results in a markdown format:
    "{text}"
    CONCISE SUMMARY:"""
    # prompt_template = """Write a summary for each chapter of the following PDF. The summary for each chapter should include
    # a detailed and at least a 150-word summary of the chapter. Focus especially on chapter 3-5, and discuss the results of the PDF.
    # "{text}"
    # CONCISE SUMMARY:"""
    prompt = PromptTemplate.from_template(prompt_template)


    loader = PyPDFLoader(file_path)
    docs = loader.load()

    llm = ChatOpenAI(temperature=0, model_name="gpt-4-1106-preview")
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")
#
    return stuff_chain.run(docs)

def traverse_directory_pathlib(directory):
    path = Path(directory)
    files = list(path.rglob("*"))
    # num_pdfs = len(files)

    for x in range(17, 20):
        file_path = str(files[x])

        # summarize PDF
        summary = summarize(file_path)

        filename = str(files[x]).split("\\")[1].split(".")[0]
        with open(f'ps1/{filename}.txt', 'w') as file:
            try:
                file.write(summary)
            except:
                print("shit")
        print(filename)


# traverse_directory_pathlib("./pdfs")
print(summarize("./pdfs/Baybáyin-Script-Translation-to-Tagalog-Using-LeNet-CNN-with-Real-time-Recognition-on-OpenCV.pdf"))