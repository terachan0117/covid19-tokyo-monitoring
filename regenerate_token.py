import pandas as pd
from janome.tokenizer import Tokenizer
import re

def reGenerateToken():
    df = pd.read_csv("data/monitoring_comments.csv", header=None, skiprows=1, encoding="utf_8_sig")
    df_token = pd.DataFrame(index=[], columns=['meeting_no', 'monitoring_index', 'token'])
    for row in df.itertuples(name=None):
        meeting_no = row[1]
        monitoring_index = row[3]
        t = Tokenizer()
        tokens = t.tokenize(row[4])
        for token in tokens:
            if not re.search(r'[、。I,%％~～#＃※\\\(\)\.\-\/]', token.surface) and token.surface not in ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ']:
                word_category = token.part_of_speech.split(',')[0]
                word_type = token.part_of_speech.split(',')[1]
                if word_category == '名詞' and word_type != '数'and word_type != '代名詞' and word_type != '非自立' and word_type != '接尾':
                    df_token.loc[len(df_token.index)] =  [meeting_no, monitoring_index, token.surface]
    df_token.to_csv('data/monitoring_comments_token.csv', index=False, encoding='utf-8-sig')

def main():
    reGenerateToken()

if __name__ == '__main__':
    main()