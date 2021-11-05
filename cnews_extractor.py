import argparse
from articles_data import Articles
    
def proceed(word_to_search, max_size_result):
    research = Articles(word_to_search, max_size_result)
    research.extract_url()
    research.extract_articles_data(max_size_result)
    research.save_to_iramuteq_txt_files()
    research.save_to_json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CNEWS text extractor')
    parser.add_argument('word_to_search', type=str, help='initialize and feed ES db')
    parser.add_argument('--max_size_result', type = int, default = 500)
    args = parser.parse_args()
    proceed(args.word_to_search, args.max_size_result)
    