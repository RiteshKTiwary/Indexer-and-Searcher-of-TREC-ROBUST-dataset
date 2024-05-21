# Indexer-and-Searcher-of-TREC-ROBUST-dataset
* Both Indexer and Searcher use Python library: Pylucene
* Dataset: TREC-ROBUST dataset
* Final ouput gives standard IR evaluation methods: 1) ndcg@20 and 2) MRR
# Indexing
* run mtc2224-indexer.py for indexing as:\
_python3 mtc2224-indexer.py \ \
/path/to/trec-robust-collection/ \ \
/path/to/directory/where/index/should/be/stored_
# Searching
* Two codes are provided: 1) mtc2224-searcher.py and mtcs2224-searcher.py
* mtc___ uses default scoring functions(like BM25) for scoring queries and documents.
* mtcs___ uses custom scoring function provided in paper **"Truncated Models for Probabilistic Weighted Retrieval"**.
* For mtc___, use command as:\
_python3 mtc2224-searcher.py \ \
/path/to/query/files/ \ \
/path/to/index/  \ \
/path/to/output/file <rollno>_\
 It's output is generating a qrel file in the form: {query_num} Q0 {doc_id} 0 {score} {roll_no}
* I have attached an output with the name as _outputFile_.
* For mtcs___, use command as:\
_python3 mtcs2224-searcher.py \ \
/path/to/query_dir \ \
/path/to/index_dir \ \
/path/to/output_file.txt <rollno> \ \
--tau1 0.5 \ \
--tau2 0.5 \ \
--k1 2 \ \
--k2 2 \ \
--alpha 0.5_ \
**Since this code is not giving proper output as expected so any suggestions are welcome from your side.**
# Results
* Given results are generated using output qrel of mtc___.
 
* **For ROBUST qrel:**\
_python3 -m pyserini.eval.trec_eval \ \
-m ndcg_cut.20 \ \
-m recip_rank \ \
/path/to/trec678rb/qrels/robust_601-700.qrel \ \
/path/to/qrel-generated_ 
* Output for the ROBUST is as: \
recip_rank     	all	    0.6901 \
ndcg_cut_20     all	    0.3821

* **For TREC678:**\
_python3 -m pyserini.eval.trec_eval \ \
-m ndcg_cut.20 \ \
-m recip_rank \ \
/path/to/trec678rb/qrels/trec678_301-450.qrel \ \
/path/to/qrel-generated_ 
* Output for the TREC678 is as: \
recip_rank     	all	    0.6400 \
ndcg_cut_20     all	    0.4131
