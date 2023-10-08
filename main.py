import dotenv
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain

dotenv.load_dotenv()

loader = PyPDFLoader("./test.pdf")
docs = loader.load_and_split()

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
chain = load_summarize_chain(llm, chain_type="stuff")

print(chain.run(docs))