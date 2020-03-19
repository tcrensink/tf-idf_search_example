import csv
from itertools import groupby, chain
import time
DATA_PATH = "school_data.csv"
SCHOOL_NAME_FIELD = 'SCHNAM05'
CITY_FIELD = "LCITY05"
STATE_FIELD = "LSTATE05"
SCHOOL_ID_FIELD = "NCESSCH"
"""
Use modified tf-idf algorithm (term frequency increases score by ~0.1% rather than sum):

1) Tokenize all school names, cities, states for each record
2) Create (modified) term-freqency dict, with term keys and score for each record:
    tf_dict = {
        term: {
            school_id1: score1,
            school_id2: score2
        }
    }
3) Create a separate inverse document freqeuncy dict for each term
4) Generate query results.  Sum the tf*idf values for each search term for each matching record
5) Return top n (3) scores.
Modifications not implemented:
6) Use separate term-frequency dict for each field (school name, city, state).  Increase score
value with number of fields matched, as most queries include both school name and city or state.
7) For query tokens with no term match (e.g. typos), add partial match values discounted by levenshtein/word length
"""


class SchoolSearch(object):
    """Search school records from query string."""

    def __init__(self, data_path=DATA_PATH):

        with open(data_path, newline="") as fp:
            reader = csv.DictReader(fp)
            self.records_dict = {}
            self.tf_dict = {}

            for record in reader:
                record_id = record[SCHOOL_ID_FIELD]
                self.records_dict[record[SCHOOL_ID_FIELD]] = record

                # get token list from record
                tokens = list(
                    chain(
                        tokenize_str(record[SCHOOL_NAME_FIELD]),
                        tokenize_str(record[CITY_FIELD]),
                        tokenize_str(record[STATE_FIELD])
                    )
                )
                update_tf_dict(self.tf_dict, record_id, tokens)
        self.idf_dict = {k: 1 / len(v) for k, v in self.tf_dict.items()}
        self.query_results_cache = {}

    def search_schools(self, query_str, n=3):
        """Search school records with query string."""
        t_start = time.time()

        if query_str in self.query_results_cache:
            results = self.query_results_cache[query_str]
        else:
            query_tokens = tokenize_str(query_str)
            match_dict = {}
            for token in query_tokens:
                try:
                    for record, value in self.tf_dict[token].items():
                        hit_value = value * self.idf_dict[token]
                        try:
                            match_dict[record] += hit_value
                        except KeyError:
                            match_dict[record] = hit_value
                except KeyError:
                    # ignore tokens not in tf_dict
                    pass

            top_matches = sorted(
                match_dict.items(), key=lambda x: x[1], reverse=True
            )[0:n]

            results = [(self.records_dict[match[0]], match[1]) for match in top_matches]
            self.query_results_cache[query_str] = results

        delta_t = round(time.time() - t_start, 4)
        print(f'Results for "{query_str}" (search took: {delta_t}s)')
        for j, result in enumerate(results):
            result_str = f"{result[0][SCHOOL_NAME_FIELD]}\n{result[0][CITY_FIELD]}, {result[0][STATE_FIELD]}"
            # print(f"{j+1}. {result_str}, {result[1]}")
            print(f"{j+1}. {result_str}")
        print("\n")


def update_tf_dict(tf_dict, record_id, token_list):
    """Update term frequency dict for given record_id, list of tokens."""
    for token in token_list:
        try:
            tf_dict[token][record_id] *= 1.001
        except KeyError:
            try:
                tf_dict[token][record_id] = 1
            except KeyError:
                tf_dict[token] = {}
                tf_dict[token][record_id] = 1


def tokenize_str(token_str):
    """Return list of tokens from raw string."""
    token_list = token_str.lower().split(" ")
    tokens = [token.strip() for token in token_list]
    return tokens


if __name__ == "__main__":

    s_search = SchoolSearch()
    s_search.search_schools(query_str="elementary school highland park")
    s_search.search_schools(query_str="jefferson belleville")
    s_search.search_schools(query_str="riverside school 44")
    s_search.search_schools(query_str="granada charter school")
    s_search.search_schools(query_str="foley high alabama")
    s_search.search_schools(query_str="KUSKOKWIM")
