import os
import requests
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain.chains import create_retrieval_chain

# Get API key
load_dotenv(find_dotenv())
os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')

# Text Processing Steps
def split_by_chapters(html):
    soup = BeautifulSoup(html, "html.parser")
    chapters = []
    for chapter in soup.find_all("div", class_="chapter"):
        title = chapter.find("h2")
        chapter_text = ""
        for paragraph in chapter.find_all("p"):
            chapter_text += paragraph.text.strip() + "\n"  # Add newline between paragraphs
        chapter_data = {"title": title.text.strip() if title else f"Chapter {len(chapters) + 1}",
                        "text": chapter_text.strip()}
        chapters.append(chapter_data)
    return chapters[1:]

# Prompt Template (tailored for chapter summaries)
template = """Provide a five sentence summary of the text based on the provided context: <context> {context} </context> The objective is to create concise and informative summaries capturing the main points of the chapter. """

# Language Model Interface
llm = ChatOpenAI()
output_parser = StrOutputParser()

# Load Book Chapters (Assuming HTML format)
prompt = ChatPromptTemplate.from_template(template)
# Combine prompt generation with LLM for summaries
document_chain = create_stuff_documents_chain(llm, prompt)

# Text Embedding and Vector Store
embeddings = OpenAIEmbeddings()

def generate_chapter_summaries(url):
    response = requests.get(url)
    html_content = response.text
    chapters = split_by_chapters(html_content)
    responses = []
    for chapter in chapters:
        responses.append([chapter["title"], document_chain.invoke({"context": [Document(page_content=chapter["text"])]})])
    return responses