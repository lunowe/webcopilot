import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_text_splitters import CharacterTextSplitter

import os

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

os.environ["OPENAI_API_KEY"] = api_key


class Chatbot:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
        self.map_template = """The following is a set of documents
        {docs}
        Based on this list of docs, please identify the main themes 
        Helpful Answer:"""
        self.reduce_template = """The following is set of summaries:
        {docs}
        Take these and distill it into a final, consolidated summary of the main themes. 
        Helpful Answer:"""

    def create_map_reduce_chain(self, docs):
        map_prompt = PromptTemplate.from_template(self.map_template)
        map_chain = LLMChain(llm=self.llm, prompt=map_prompt)
        reduce_prompt = PromptTemplate.from_template(self.reduce_template)
        reduce_chain = LLMChain(llm=self.llm, prompt=reduce_prompt)
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="docs"
        )
        reduce_documents_chain = ReduceDocumentsChain(
            # This is final chain that is called.
            combine_documents_chain=combine_documents_chain,
            # If documents exceed context for `StuffDocumentsChain`
            collapse_documents_chain=combine_documents_chain,
            # The maximum number of tokens to group documents into.
            token_max=4000,
        )

        map_reduce_chain = MapReduceDocumentsChain(
            # Map chain
            llm_chain=map_chain,
            # Reduce chain
            reduce_documents_chain=reduce_documents_chain,
            # The variable name in the llm_chain to put the documents in
            document_variable_name="docs",
            # Return the results of the map steps in the output
            return_intermediate_steps=False,
        )

        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0
        )
        split_docs = text_splitter.split_documents(docs)

        result = map_reduce_chain.invoke(split_docs)

        print(result)


    def load_web_docs(self, url):
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs

    def split_docs(self, docs):
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0
        )
        split_docs = text_splitter.split_documents(docs)


    def setup_summary_chain(self, type):
        prompt_template = f"""Write a {type} summary of the following:
        "{{text}}"
        IF the text is in german, translate the summary to german.
        {type.upper()} SUMMARY:"""

        prompt = PromptTemplate.from_template(prompt_template)

        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")

        return stuff_chain

if __name__ == "__main__":
    chatbot = Chatbot()
    docs = chatbot.load_web_docs("https://de.wikipedia.org/wiki/Fu%C3%9Fball-Weltmeisterschaft_2010")
    chain = chatbot.setup_summary_chain("detailed")
    # chatbot.create_map_reduce_chain(docs)

    # loader = WebBaseLoader("https://de.wikipedia.org/wiki/Fu%C3%9Fball-Weltmeisterschaft_2010")
    # docs = loader.load()

    # llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
    # chain = load_summarize_chain(llm, chain_type="stuff")

    # result = chain.invoke(docs)

    print(chain.invoke(docs)["output_text"])