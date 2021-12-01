import argparse
from corpus_converter import IramuteqConverter
from extractor import CNewsExctraction
from articles_data import Articles
    
def proceed(word_to_search, max_size_result):
    corpus_data = Articles(word_to_search, max_size_result)
    extractor = CNewsExctraction(corpus_data)
    iramuteq_converter = IramuteqConverter(corpus_data)
    extractor.extract_urls()
    extractor.extract_articles_data()
    iramuteq_converter.save_to_iramuteq_txt_files()
    # corpus_data.save_to_json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CNEWS text extractor')
    parser.add_argument('word_to_search', type=str, help='initialize and feed ES db')
    parser.add_argument('--max_size_result', type = int )
    args = parser.parse_args()
    proceed(args.word_to_search, args.max_size_result)
    