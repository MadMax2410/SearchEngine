#!/usr/bin/env python

'''
This is a search engine developed using two different approaches: LSI and Tf-Idf.
You can choose which method to run just specifying in one of the constructor parameter.
You'll need to have a server with running FreeLing
'''

from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from nltk import wordpunct_tokenize
from nltk.tokenize import sent_tokenize
import string
import collections
import subprocess
import json
import ast
import operator
import sys
from os import listdir
from os.path import isfile, join
from tfidf import TfIdf


class SkyScanner:
    urls = {'formnet.txt': 'https://www.entrepreneur.com/formnet',
            'kuldip-maity.txt': 'https://www.entrepreneur.com/author/kuldip-maity',
            'bootstrapping.txt': 'https://www.entrepreneur.com/encyclopedia/bootstrapping',
            'cash-flow-statement.txt': 'https://www.entrepreneur.com/encyclopedia/cash-flow-statement',
            'equity-financing.txt': 'https://www.entrepreneur.com/encyclopedia/equity-financing',
            'financial-statement.txt': 'https://www.entrepreneur.com/encyclopedia/financial-statement',
            'equity-crowdfunding.txt': 'https://www.entrepreneur.com/topic/equity-crowdfunding',
            '4.txt': 'https://www.entrepreneur.com/topic/startup-funding/4'}


    def __init__(self,
                 project_dir='/home/peregfe/projects/Entrepreneur',
                 num_topics=100,
                 threshold=0.3,
                 model_name='lsi',
                 remove_sw=True,
                 remove_punct=True,
                 remove_hl=True):
        '''
        Class contructor
        :param project_dir: String with the directory where the project is 
        :param num_topics: Integer which tells the number of topics to the LSI model
        :param threshold: Float that identifies the minimum score needed to be considered as a possible retrieved document
        :param model_name: String with one of these values: 'lsi' or 'tfidf' which tells to the system which model to use
        :param remove_sw: Boolean varible that tells whether the Stopwords will be deleted or not
        :param remove_punct: Boolean varible that tells whether the punctuation symbols will be deleted or not
        :param remove_hl: Boolean varible that tells whether the hapax legomenon will be deleted or not
        '''
        self.project_dir = project_dir
        self.threshold = threshold

        self.init_variables()
        self.ext_lang, self.stopwords_set = self.init_languages()
        for language in self.ext_lang.keys():
            print('\nLoading the model for ' + language + '...')
            self.language = language
            self.init_model(language, num_topics, model_name, remove_sw, remove_punct, remove_hl)



    def init_variables(self):
        '''
        It initializes all the model variables
        :return: None
        '''
        self.stopWords = {}
        self.punctSym = {}
        self.files_dir = {}
        self.files = {}
        self.frequency = {}
        self.dct = {}
        self.model = {}
        self.index = {}
        self.doc_index = {}
        self.query = None


    def init_model(self, language, num_topics, model_name, remove_sw, remove_punct, remove_hl):
        '''
        Function that loads the model in the given language
        :param language: String which tells which model language will be load
        :param num_topics: Integer which tells the number of topics to the LSI model
        :param model_name: String with one of these values: 'lsi' or 'tfidf' which tells to the system which model to use
        :param remove_sw: Boolean varible that tells whether the Stopwords will be deleted or not
        :param remove_punct: Boolean varible that tells whether the punctuation symbols will be deleted or not 
        :param remove_hl: Boolean varible that tells whether the hapax legomenon will be deleted or not
        :return: None
        '''
        if remove_sw:
            self.stopWords[language] = set(stopwords.words(language))
        else:
            self.stopWords[language] = set()
        if remove_punct:
            self.punctSym[language] = string.punctuation + "·€£$“”``''«»¿¡…"
        else:
            self.punctSym[language] = set()

        if (model_name != 'lsi' and model_name != 'tfidf'):
            print('ERROR: The model has to be either \'lsi\' or \'tfidf\'')
            sys.exit()
        if model_name == 'tfidf':
            self.threshold = 0
        self.model_name = model_name

        # getting the terms frequency
        self.files_dir[language] = join(self.project_dir, 'data/lemmas/' + self.ext_lang[language])
        self.files[language], self.frequency[language] = self.get_terms_frequency()

        # building the dictionary
        if remove_hl:
            self.dct[language], self.files_dir[language] = self.remove_hapax_legomenon()
        else:
            self.dct[language] = self.build_dictionary()

        # building the model
        self.model[language], self.index[language], self.doc_index[language] = self.build_model(num_topics)


    def init_languages(self):
        '''
        It tells which languages will be used by the model
        :return: 
             ext_lang: dictionary whith the language name and its ISO code
             stopwords_set: dictionary with a set of stopwords for each used language
        '''
        ext_lang = {'english': 'en',
                    'spanish': 'es'}
        stopwords_set = {}
        for language in ext_lang.keys():
            stopwords_set[language] = set(stopwords.words(language))
        return ext_lang, stopwords_set


    def guess_language(self, text):
        '''
        It guesses the language in which the given text is written
        :param text: String with the text whose language want to be detected
        :return: A string with the name of the detected language
        '''
        languages_ratios = {}
        tokens = wordpunct_tokenize(text)
        words = [word.lower() for word in tokens]
        for language in self.stopwords_set.keys():
            words_set = set(words)
            common_elements = words_set.intersection(self.stopwords_set[language])
            languages_ratios[language] = len(common_elements)  # language "score"

        languages = sorted(languages_ratios.items(), key=operator.itemgetter(1), reverse=True)
        if languages[0][1] <= languages_ratios['english']:
            return 'english'
        return languages[0][0]


    def run_query(self, query):
        '''
        It sends the given query to the model
        :param query: Query to be sent to the model
        :return: The documents sorted by the proximity to the given query
        '''
        self.query = query
        self.language = self.guess_language(query)
        query = self.clean_query(query)
        if self.model_name == 'lsi':
            return self.run_lsi_query(query)
        elif self.model_name == 'tfidf':
            return self.run_tfidf_query(query)


    def run_lsi_query(self, query):
        '''
        It sends the given query to the LSI model
        :param query: Query to be sent to the model
        :return: The documents sorted by the proximity to the given query
        '''
        vec_bow = self.dct[self.language].doc2bow(query)  # looks up the 'query' terms in the dictionary
        vec_lsi = self.model[self.language][vec_bow]  # converts the query to LSI space to get the most probable topic

        # gets a sorted list of the most relevant documents related to the given query
        sims = self.index[self.language][vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        return sims


    def normalize_scores(self, sims):
        '''
        It normalizes the scores in the given results
        :param sims: List where each element have a list of two elements:
            0: String with the name of the file
            1: Float with the score
        :return: The same list but with the values normalized from 0 to 1
        '''
        max_score = sims[0][1]
        return [[x[0], x[1] / max_score] for x in sims]


    def run_tfidf_query(self, query):
        '''
        It sends the given query to the Tf-Idf model
        :param query: Query to be sent to the model
        :return: The documents sorted by the proximity to the given query
        '''
        sims = self.model[self.language].similarities(query)
        sims.sort(key=lambda x: x[1], reverse=True)
        # return self.normalize_scores(sims)
        return sims


    def get_lsi_output(self, doc, score):
        '''
        It builds the JSON object to be sent to the interface
        :param sims: The documents sorted by the proximity to the given query
        :return: The JSON object
        '''
        file_path = self.doc_index[self.language][doc].replace(self.files_dir[self.language].split('/')[-2:-1][0], 'documents')
        file_name = file_path.split('/')[-1]
        file_path = '/'.join(file_path.split('/')[:-1]) + '/article/' + file_name
        if file_name in self.urls:
            url = self.urls[file_name]
        else:
            url = 'https://www.entrepreneur.com/article/' + file_path.split('/')[-1][:-4]
        return file_path, url


    def get_tfidf_output(self, doc, score):
        if doc in self.urls:
            url = self.urls[doc]
        else:
            url = 'https://www.entrepreneur.com/article/' + doc[:-4]
        file_path = join(self.project_dir, 'data/documents/' + self.ext_lang[self.language] + '/article/' + doc)
        return file_path, url


    def get_output(self, sims):
        '''
        It builds the JSON object to be sent to the interface
        :param sims: The documents sorted by the proximity to the given query
        :return: The JSON object
        '''
        if self.query == None:
            print("ERROR: You have to send a query first")
            pass

        output = []
        i = 0
        for sim in sims:
            doc = sim[0]
            score = sim[1]
            if score > self.threshold and i < 10:
                if self.model_name == 'tfidf':
                    file_path, url = self.get_tfidf_output(doc, score)
                elif self.model_name == 'lsi':
                    file_path, url = self.get_lsi_output(doc, score)
                with open(file_path) as f:
                    lines = f.readlines()
                    title = lines[0].strip()
                    snippet = self.get_snippet(file_path, self.query)
                    output.append({'url': url, 'title': title, 'snippet': snippet})
                i += 1
        return json.dumps(output)



    def get_output_old(self, sims):
        '''
        It builds the JSON object to be sent to the interface
        :param sims: The documents sorted by the proximity to the given query
        :return: The JSON object
        '''
        if self.query == None:
            print("ERROR: You have to send a query first")
            pass

        output = []
        i = 0
        for sim in sims:
            doc = sim[0]
            score = sim[1]
            if score > self.threshold and i < 10:
                file_path = self.doc_index[doc].replace(self.files_dir.split('/')[-2:-1][0], 'documents')
                file_name = file_path.split('/')[-1]
                file_path = '/'.join(file_path.split('/')[:-1]) + '/article/' + file_name
                if file_name in self.urls:
                    url = self.urls[file_name]
                else:
                    url = 'https://www.entrepreneur.com/article/' + file_path.split('/')[-1][:-4]
                with open(file_path) as f:
                    lines = f.readlines()
                    title = lines[0].strip()
                    snippet = self.get_snippet(file_path, self.query)
                    output.append({'url': url, 'title': title, 'snippet': snippet})
                i += 1
        return json.dumps(output)


    def print_results(self, sims):
        '''
        It shows the title and summary of the closest 10 results for the given query
        :param sims: The documents sorted by the proximity to the given query
        :return: True
        '''
        i = 0
        for sim in sims:
            score = sim[1]
            doc = sim[0]
            if score > self.threshold and i < 10:
                file_path = self.doc_index[doc].replace(self.files_dir.split('/')[-2:-1], 'documents')
                file_path = '/'.join(file_path.split('/')[:-1]) + '/article/' + file_path.split('/')[-1]
                print(score, file_path)
                with open(file_path) as f:
                    print(f.readlines()[:2], '\n')
                i += 1
        return True


    def build_dictionary(self):
        '''
        To create a dictionary with all the corpus terms
        :return: Dictionary with all the corpus terms
        '''
        print('\tBuilding the dictionary...')
        dct = corpora.Dictionary([[]])
        for file_path in self.files[self.language]:
            with open(file_path) as f:
                text = [term for term in f.readline().lower().split() if self.frequency[self.language][term] > 1]
                dct.add_documents([text])
        return dct


    def remove_hapax_legomenon(self):
        '''
        To remove all the terms which appear just once in the whole corpus and 
        create a dictionary with all the corpus terms
        :return: 
            dtc: Dictionary with all the corpus terms
            clean_dir: The files directory to build the model
        '''
        print('\tBuilding the dictionary and removing the hapax legomenon...')
        clean_dir = join(self.project_dir, 'data/clean_texts/' + self.ext_lang[self.language])
        dct = corpora.Dictionary([[]])
        for file_path in self.files[self.language]:
            file_name = file_path.split('/')[-1]
            with open(file_path) as f:
                text = [term for term in f.readline().lower().split() if self.frequency[self.language][term] > 1]
                dct.add_documents([text])
                with open(join(clean_dir, file_name), 'w') as f:
                    f.write(' '.join(text))
        return dct, clean_dir


    def get_terms_frequency(self):
        '''
        To get the corpus terms frequency
        :param files_dir: Directory where all the text files are
        :return: 
            files: The corpus files
            frequency: The terms frequency
        '''
        print('\tGetting the terms frequency...')
        files = [join(self.files_dir[self.language], f) for f in listdir(self.files_dir[self.language]) if isfile(join(self.files_dir[self.language], f))]
        frequency = collections.Counter()
        for file_path in files:
            with open(file_path) as f:
                text = [term for term in f.readline().lower().split() if term not in self.stopWords[self.language] and term not in self.punctSym[self.language]]
                frequency += collections.Counter(text)
        return files, frequency


    def build_model(self, num_topics):
        '''
        It builds either a LSI model or a Tf-Idf model
        :param files_dir: Directory where all the files which will build the model are
        :param num_topics: Number of topics for the model
        :return: The model index
        '''
        print('\tBuilding the model...')
        files = [join(self.files_dir[self.language], f) for f in listdir(self.files_dir[self.language]) if isfile(join(self.files_dir[self.language], f))]
        if self.model_name == 'lsi':
            return self.build_lsi_model(files, num_topics)
        elif self.model_name == 'tfidf':
            return self.build_tfidf_model(files), None, None # The None values are set to return the same format as the LSI model


    def build_tfidf_model(self, files):
        '''
        It builds the Tf-Idf model
        :param files: List of files of the corpora
        :return: A Tf-Idf object with the model loaded
        '''
        tfidf = TfIdf()
        for file_path in files:
            with open(file_path) as f:
                doc_name = file_path.split('/')[-1]
                doc_text = f.readline().split()
                tfidf.add_document(doc_name, doc_text)
        return tfidf


    def build_lsi_model(self, files, num_topics):
        '''
        It builds the LSI model
        :param files_dir: Directory where all the files which will build the model are
        :param num_topics: Number of topics for the model
        :return: The model index
        '''
        doc_index = {}
        corpus = []
        for i, file_path in enumerate(files):
            doc_index[i] = file_path
            with open(file_path) as f:
                text = f.readline()
                corpus.append(self.dct[self.language].doc2bow(text.split()))  # token_id token_frequency_in_this_text
        corpora.MmCorpus.serialize('corpus_' + self.ext_lang[self.language] + '.mm',
                                   corpus)  # text_id token_id(alphabetically_sorted) token_frequency_in_this_text

        lsi = models.LsiModel(corpus, id2word=self.dct[self.language], num_topics=num_topics)
        index = similarities.MatrixSimilarity(lsi[corpus])
        return lsi, index, doc_index


    def clean_query(self, query):
        '''
        It adapts the given query to the corpus terms
        :param query: The query to be adapted
        :return: The properly format query
        '''
        query = query.replace("’", "'")
        query = self.lemmatize_text(query)
        query = query.replace("crowd funding", "crowd_funding")
        query = query.replace("crowdfunding", "crowd_funding")
        query = query.replace("crowd fund", "crowd_fund")
        query = query.replace("crowdfund", "crowd_fund")
        query = query.replace("setup", "set up")
        query = query.replace("set-up", "set up")
        query = [term for term in query.split() if term not in self.stopWords[self.language] and term not in self.punctSym[self.language]]
        return query


    def get_output_as_list_dict(self, json):
        '''
        It converts the JSON string retrieval into a list of dictionaries where each dictionary represent a retrieval
        :param json: String in a JSON format
        :return: List of dictionaries
        '''
        output = []
        docs = json.split(', {')
        i = 0
        for doc in docs:
            i += 1
            if len(docs) == 1:
                if(doc == '[]'):
                    print('Your search did not match any documents.')
                else:
                    output.append(ast.literal_eval(doc[1:-1]))
            elif i == 1:
                output.append(ast.literal_eval(doc[1:]))
            elif i < len(docs):
                output.append(ast.literal_eval('{' + doc))
            else:
                output.append(ast.literal_eval('{' + doc[:-1]))
        return output


    def lemmatize_text(self, text):
        '''
        It gets all the lemmas of a given text.
        You'll need to have FreeLing running in the server in the same port (analyze -f es.cfg --server --port 50005 &)
        :param text: Text to be lemmatized
        :return: A string with the text lemmatized
        '''
        if self.language == 'english':
            bashCommand = "echo \"" + text + "\" | analyzer_client 50005"
        elif self.language == 'spanish':
            bashCommand = "echo \"" + text + "\" | analyzer_client 50006"
        process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True)
        output = process.communicate()
        terms = str(output[0][:-1]).split('\\n')
        lemmatized = ""
        for term in terms:
            part = term.split()
            if len(part) == 4:
                if part[2] == 'W':
                    lemmatized += part[0] + ' '
                else:
                    lemmatized += part[1] + ' '
        return lemmatized[:-1]


    def get_positions(self, query, text):
        '''
        It finds the terms position in the text where the query terms match
        :param query: String of text with the terms to look
        :param text: String of text where the terms from the query will be looked
        :return: A list with the position of the terms in the text which match with the ones in the query
        '''
        i = 0
        match = []
        for tterm in text.split():
            for qterm in query.split():
                if tterm == qterm:
                    match.append(i)
            i += 1
        return match


    def get_n_best_sentences(self, terms_pos, n):
        '''
        It gets the number of the n sentences which have more terms in common with the query
        :param terms_pos: two-dimensional list where the first dimension represent each sentence position in the text 
        and the second the terms position which matched with the query  
        :param n: Number of sentences to retrieve
        :return: A list with the number of the sentences which have more terms in common with the query
        '''
        matches = {}
        i = 0
        for sentence in terms_pos:
            matches[i] = len(sentence)
            i += 1
        best = sorted(matches.items(), key=operator.itemgetter(1), reverse=True)
        return [s[0] for s in best[:3]]


    def get_text(self, sentences, best):
        '''
        It retrieves and concatenates the n sentences which have more terms in common with the query
        :param sentences: List of sentences from the original document
        :param best: List with the position of the chosen sentences in the original text
        :return: A string with the n best sentences concatenated separating them by ellipsis
        '''
        snippet = ''
        j = 0
        for i in sorted(best):
            if j == 0:
                snippet += sentences[i]
            elif i == (j+1):
                snippet += ' ' + sentences[i]
            else:
                snippet += ' [...] ' + sentences[i]
            j = i
        if snippet[-1] == '.':
            snippet += '..'
        else:
            snippet += '...'
        return snippet


    def get_snippet(self, file_path, l_query):
        '''
        It builds the snippets from the given document which best match with the given query
        :param file_path: Local path where the text document is
        :param l_query: String with the lemmatized query
        :return: A string with the n best sentences concatenated separating them by ellipsis
        '''
        with open(file_path) as f:
            lines = f.readlines()
            if len(lines) == 3:
                text = lines[2]  # read only the body of the document
            else:
                text = ' '.join(lines)
            sent_tokenize_list = sent_tokenize(text)
            terms_pos = []
            for sentence in sent_tokenize_list:
                l_sent = self.lemmatize_text(sentence)
                pos = self.get_positions(l_query, l_sent)
                terms_pos.append(pos)
            n = 3
            best = self.get_n_best_sentences(terms_pos, n)
            return self.get_text(sent_tokenize_list, best)


    def get_snippets(self, retrievals, query):
        '''
        It builts the snippets from a list of documents and a given query
        :param retrievals: List of tuples where the first position in each tuple is the document identifier and 
        the second the obtained scored for the given query
        :param query: String with the query sent to the system
        :return: List of the snippets for all the documents which got and score above the threshold
        '''
        l_query = self.lemmatize_text(query)
        snippets = []
        i = 0
        for retrieval in retrievals:
            doc = retrieval[0]
            score = retrieval[1]
            if score > self.threshold and i < 10:
                file_path = self.doc_index[doc].replace(self.files_dir.split('/')[-2:-1][0], 'documents')
                file_path = '/'.join(file_path.split('/')[:-1]) + '/article/' + file_path.split('/')[-1]
                snippet = self.get_snippet(file_path, l_query)
                snippets.append(snippet)
        return snippets
