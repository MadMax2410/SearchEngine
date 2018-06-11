# SearchEngine
This is a search engine developed using two different approaches: LSI and Tf-Idf. You can choose which method to run just specifying in one of the constructor parameter (```model_name = 'lsi'``` or ```'tfidf'```). 

You'll need to:
1. Scrape a corpora. You can do it using *scrapper.py* script (it needs *scrapy* to be installed): ```scrapy runspider scrapper.py```
2. have a server with [FreeLing](http://nlp.lsi.upc.edu/freeling/index.php/node/1) running.
    - Start the analyzer in a terminal (tell to the system the config file for the language you want to run (*es.cfg*) and a port): ```analyze -f es.cfg --server --port 50005 &```
    - Call the analyzer (it is called from the code in *SkyScanner.py*): ```analyzer_client 50005 <myinput >myoutput```
3. Run *SkyScanner*. 
    - ```se = SkyScanner() # By default, it is instantiated in *LSI* mode.```
    - ```retrieved_documents = se.run_query('my query')```
    - ```se.get_output(retrieved_documents)```
