import os
import sys
import lucene
from bs4 import BeautifulSoup
from java.io import File
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import FSDirectory
import org.apache.lucene.document as document

def index_documents(docs_dir, index_dir):
    lucene.initVM()

    index_path = File(index_dir).toPath()
    index_dir = FSDirectory.open(index_path)

    analyzer = EnglishAnalyzer()
    writer_config = IndexWriterConfig(analyzer)
    writer = IndexWriter(index_dir, writer_config)

    def index_doc(doc_id, content):
        doc = document.Document()
        doc.add(document.Field("DOC_ID", doc_id, document.TextField.TYPE_STORED))
        doc.add(document.Field("CONTENT", content, document.TextField.TYPE_STORED))
        writer.addDocument(doc)

    def close_writer():
        writer.close()

    for root, _, files in os.walk(docs_dir):
        for file in files:
            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
                soup = BeautifulSoup(file_content, 'html.parser')
                for doc in soup.find_all('doc'):
                    doc_id = doc.find('docno').get_text().strip()
                    text_tag = doc.find('text')
                    content = text_tag.get_text().strip() if text_tag else ''
                    index_doc(doc_id, content)

    close_writer()
    print("Indexing complete.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 mtc2224-indexer.py /path/to/trec-robust-collection/ /path/to/directory/where/index/should/be/stored")
        sys.exit(1)

    docs_dir = sys.argv[1]
    index_dir = sys.argv[2]

    index_documents(docs_dir, index_dir)
