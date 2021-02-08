import pandas as pd
from janome.tokenizer import Tokenizer
import re

def reGenerateToken():
    df = pd.read_csv("data/monitoring_comments_split.csv", header=None, skiprows=1, encoding="utf_8_sig")
    df_token = pd.DataFrame(index=[], columns=['meeting_no', 'meeting_date', 'monitoring_index', 'line_number', 'token', 'part_of_speech', 'part_of_speech2', 'part_of_speech3', 'part_of_speech4', 'infl_type', 'base_form'])
    for row in df.itertuples(name=None):
        meeting_no = row[1]
        meeting_date = row[2]
        monitoring_index = row[3]
        line_number = row[4]
        t = Tokenizer()
        tokens = t.tokenize(row[5])
        for token in tokens:
            if not re.search(r'[、。I,%％~～#＃※\\\(\)\.\-\/]', token.surface) and token.surface not in ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ']:
                word_category = token.part_of_speech.split(',')[0]
                word_type = token.part_of_speech.split(',')[1]
                if word_category == '名詞' and word_type != '数'and word_type != '代名詞' and word_type != '非自立' and word_type != '接尾':
                    df_token.loc[len(df_token.index)] =  [meeting_no, meeting_date, monitoring_index, line_number, token.surface] + token.part_of_speech.split(',') + [token.infl_type, token.base_form]
    df_token.to_csv('data/monitoring_comments_token.csv', index=False, encoding='utf-8-sig')

def main():
    reGenerateToken()

if __name__ == '__main__':
    main()