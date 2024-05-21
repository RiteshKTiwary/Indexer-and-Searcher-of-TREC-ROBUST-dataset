import os
import sys
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import FSDirectory
from bs4 import BeautifulSoup

def escape_query(query):
    # Escape special characters for the QueryParser
    special_chars = r'\\+-&|!(){}[]^"~*?:/'
    for char in special_chars:
        query = query.replace(char, f'\\{char}')
    return query

def search_queries(query_dir, index_dir, output_file, roll_no):
    lucene.initVM()

    index_path = Paths.get(index_dir)
    directory = FSDirectory.open(index_path)
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = EnglishAnalyzer()

    queries = []

    for root, _, files in os.walk(query_dir):
        for file in files:
            if file.endswith(".xml"):
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                    soup = BeautifulSoup(file_content, 'xml')
                    for topic in soup.find_all('top'):
                        query_num = topic.find('num').get_text().strip()
                        query_text = topic.find('title').get_text().strip()
                        queries.append((int(query_num), query_text))

    # Sort queries by query number
    queries.sort()

    with open(output_file, 'w') as out_file:
        for query_num, query_text in queries:
            escaped_query_text = escape_query(query_text)
            query_parser = QueryParser("CONTENT", analyzer)
            query = query_parser.parse(escaped_query_text)

            hits = searcher.search(query, 1000).scoreDocs

            for rank, hit in enumerate(hits):
                doc = searcher.doc(hit.doc)
                doc_id = doc.get("DOC_ID")
                score = hit.score
                out_file.write(f"{query_num} Q0 {doc_id} {rank + 1} {score:.6f} {roll_no}\n")

    print("Search complete. Results saved to", output_file)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 mtc2224-searcher.py /path/to/query/files/ /path/to/index/ /path/to/output/file <rollno>")
        sys.exit(1)

    query_dir = sys.argv[1]
    index_dir = sys.argv[2]
    output_file = sys.argv[3]
    roll_no = sys.argv[4]

    search_queries(query_dir, index_dir, output_file, roll_no)
