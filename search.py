import re
import pylru


class SearchEngineBase(object):
    def __init__(self):
        pass

    def add_corpus(self, file_path):
        with open(file_path, 'r') as fin:
            text = fin.read()
        self.process_corpus(file_path, text)

    def process_corpus(self, id, text):
        raise Exception('process_corpus not implemented.')

    def search(self, query):
        raise Exception('search not implemented.')


class SimpleEngine(SearchEngineBase):
    def __init__(self):
        super(SimpleEngine, self).__init__()
        self.__id_to_texts = {}

    def process_corpus(self, id, text):
        self.__id_to_texts[id] = text

    def search(self, query):
        results = []
        for id, text in self.__id_to_texts.items():
            if query in text:
                results.append(id)
        return results


class BOWEngine(SearchEngineBase):
    def __init__(self):
        super(BOWEngine, self).__init__()
        self.__id_to_word = {}

    def process_corpus(self, id, text):
        self.__id_to_word[id] = self.parse_text_to_word(text)

    def search(self, query):
        query_words = self.parse_text_to_word(query)
        results = []
        for id, words in self.__id_to_word.items():
            if self.query_match(query_words, words):
                results.append(id)
        return results

    @staticmethod
    def parse_text_to_word(text):
        # Use regex to remove punctuation and newlines
        text = re.sub(r'[^\w ]', ' ', text)
        # To lower
        text = text.lower()
        # Generate a list of all words
        word_list = text.split(' ')
        # Remove blank words
        word_list = filter(None, word_list)
        # Return a set of words
        return set(word_list)

    @staticmethod
    def query_match(query_words, words):
        for query_word in query_words:
            if query_word not in words:
                return False
        return True


# 减少查询的量
class BOWInvertedIndexEngine(SearchEngineBase):
    def __init__(self):
        super(BOWInvertedIndexEngine, self).__init__()
        self.inverted_index = {}

    def process_corpus(self, id, text):
        words = self.parse_text_to_word(text)
        for word in words:
            if word not in self.inverted_index:
                self.inverted_index[word] = []
            self.inverted_index[word].append(id)

    def search(self, query):
        query_words = list(self.parse_text_to_word(query))
        query_words_index = list()
        for _ in query_words:
            query_words_index.append(0)

        # If a word is indexed in reverse order, return immediately.
        for query_word in query_words:
            if query_word not in self.inverted_index:
                return []

        result = []
        while True:
            # First get the index of all inverted indexes in the current state.
            current_ids = []
            for idx, query_word in enumerate(query_words):
                current_index = query_words_index[idx]
                current_inverted_list = self.inverted_index[query_word]
                # If the current index exceeds the length of the inverted list,
                # it means that the query is not in the inverted list.
                if current_index >= len(current_inverted_list):
                    return result
                current_ids.append(current_inverted_list[current_index])

            # If all the elements in the current_ids are the same, it means that the query is in the inverted list.
            if all(x == current_ids[0] for x in current_ids):
                result.append(current_ids[0])
                query_words_index = [x + 1 for x in query_words_index]
                continue

            # If not all elements are the same, increase the index of the smallest element by 1.
            min_val = min(current_ids)
            min_val_pos = current_ids.index(min_val)
            query_words_index[min_val_pos] += 1

    @staticmethod
    def parse_text_to_word(text):
        # Use regex to remove punctuation and newlines
        text = re.sub(r'[^\w ]', ' ', text)
        # To lower
        text = text.lower()
        # Generate a list of all words
        word_list = text.split(' ')
        # Remove blank words
        word_list = filter(None, word_list)
        # Return a set of words
        return set(word_list)


class LRUCache(object):
    def __init__(self, size=2):
        self.cache = pylru.lrucache(size)

    def has(self, key):
        return key in self.cache

    def get(self, key):
        return self.cache[key]

    def set(self, key, value):
        self.cache[key] = value


class BOWInvertedIndexEngineWithCache(BOWInvertedIndexEngine, LRUCache):
    def __init__(self):
        super(BOWInvertedIndexEngineWithCache, self).__init__()
        LRUCache.__init__(self)

    def search(self, query):
        if self.has(query):
            print('cache hit!')
            return self.get(query)

        result = super(BOWInvertedIndexEngineWithCache, self).search(query)
        self.set(query, result)

        return result


def main(search_engine):
    for file_path in ["./text/1.txt", "./text/2.txt", "./text/3.txt", "./text/4.txt"]:
        search_engine.add_corpus(file_path)

    while True:
        query = input("Please input query:")
        if query == "q":
            break
        results = search_engine.search(query)
        print("found {} result(s):".format(len(results)))

        for result in results:
            print(result)

# if __name__ == "__main__":
#     search_engine = SimpleEngine()
#     main(search_engine)
#     search_engine = BOWEngine()
#     main(search_engine)
#     search_engine = BOWInvertedIndexEngine()
#     main(search_engine)
#     search_engine = BOWInvertedIndexEngineWithCache()
#     main(search_engine)
