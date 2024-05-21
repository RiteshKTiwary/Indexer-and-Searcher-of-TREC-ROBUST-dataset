import os
import lucene
import math
import argparse
import xml.etree.ElementTree as ET
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser, QueryParserBase
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.index import Term
from java.nio.file import Paths

def calculate_tf(term, document):
    # Calculate term frequency of the term in the document
    term_freq = document.split().count(term)
    return term_freq

def calculate_mtc(term, collection):
    # Calculate mean term frequency (mtc) of the term in the collection
    term_count = sum(doc.split().count(term) for doc in collection)
    doc_count = len(collection)
    return term_count / doc_count if doc_count > 0 else 0

def calculate_adl(collection):
    # Calculate average document length (adl) in the collection
    total_length = sum(len(doc.split()) for doc in collection)
    doc_count = len(collection)
    return total_length / doc_count if doc_count > 0 else 0

def calculate_doc_length(document):
    # Calculate the length of the document
    return len(document.split())

def calculate_X(term, document, collection):
    tf = calculate_tf(term, document)
    mtc = calculate_mtc(term, collection)
    c = 0.001  # Free parameter, adjust as needed
    return math.log(1 + tf) / math.log(c + mtc)

def calculate_Y(term, document, collection):
    tf = calculate_tf(term, document)
    adl = calculate_adl(collection)
    doc_length = calculate_doc_length(document)
    return tf * math.log(1 + adl / doc_length)

def Ft(x, tau, k):
    if 0 <= x <= tau:
        return (1 - math.pow(1 + x, -k)) / (1 - math.pow(1 + tau, -k))
    else:
        return 0

def custom_score(query_terms, document, collection, idf_dict, alpha, tau1, tau2, k1, k2):
    score = 0
    for term in query_terms:
        idf = idf_dict.get(term, 0)
        x = calculate_X(term, document, collection)
        y = calculate_Y(term, document, collection)
        FX = Ft(x, tau1, k1)
        FY = Ft(y, tau2, k2)
        score += idf * (alpha * FX + (1 - alpha) * FY)
    return score

def parse_queries(query_dir):
    queries = []
    for filename in os.listdir(query_dir):
        if filename.endswith(".xml"):
            filepath = os.path.join(query_dir, filename)
            tree = ET.parse(filepath)
            root = tree.getroot()
            for top in root.findall('top'):
                query_num = top.find('num').text.strip()
                title = top.find('title').text.strip()
                queries.append((query_num, title))
    return queries

def escape_query(query):
    return QueryParserBase.escape(query)

def search_queries(query_dir, index_dir, output_file, roll_no, tau1, tau2, k1, k2, alpha):
    lucene.initVM()  # Initialize JVM
    index_path = Paths.get(index_dir)
    directory = FSDirectory.open(index_path)
    indexReader = DirectoryReader.open(directory)
    searcher = IndexSearcher(indexReader)
    analyzer = StandardAnalyzer()
    
    queries = parse_queries(query_dir)
    
    with open(output_file, 'w') as f_out:
        for query_num, query_text in sorted(queries, key=lambda x: int(x[0])):
            query_parser = QueryParser("TEXT", analyzer)
            escaped_query_text = escape_query(query_text)
            query = query_parser.parse(escaped_query_text)
            hits = searcher.search(query, 20).scoreDocs
            
            collection = [searcher.doc(hit.doc).get("TEXT") for hit in hits]
            idf_dict = {term: math.log(indexReader.numDocs() / (indexReader.docFreq(Term("TEXT", term)) + 1)) for term in escaped_query_text.split()}
            
            for hit in hits:
                doc_id = searcher.doc(hit.doc).get("DOCNO")
                doc_text = searcher.doc(hit.doc).get("TEXT")
                score = custom_score(escaped_query_text.split(), doc_text, collection, idf_dict, alpha, tau1, tau2, k1, k2)
                # Debug statement to check the score calculation
                print(f"Query: {query_num}, DocID: {doc_id}, Score: {score}")
                f_out.write(f"{query_num} Q0 {doc_id} 0 {score} {roll_no}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search using custom scoring function")
    parser.add_argument("query_dir", type=str, help="Directory containing query XML files")
    parser.add_argument("index_dir", type=str, help="Directory containing the Lucene index")
    parser.add_argument("output_file", type=str, help="Output file to write the search results")
    parser.add_argument("roll_no", type=str, help="Roll number to include in the output file")
    parser.add_argument("--tau1", type=float, default=0.5, help="Truncation point for X")
    parser.add_argument("--tau2", type=float, default=0.5, help="Truncation point for Y")
    parser.add_argument("--k1", type=float, default=2, help="Shape parameter for Ft function of X")
    parser.add_argument("--k2", type=float, default=2, help="Shape parameter for Ft function of Y")
    parser.add_argument("--alpha", type=float, default=0.5, help="Weight parameter alpha")

    args = parser.parse_args()

    search_queries(args.query_dir, args.index_dir, args.output_file, args.roll_no, args.tau1, args.tau2, args.k1, args.k2, args.alpha)
