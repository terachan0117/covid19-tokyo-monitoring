from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import datetime
import pandas as pd
import tabula
import re
from janome.tokenizer import Tokenizer
import numpy as np

def getLastMeetingNo():
    df = pd.read_csv('data/monitoring_comments.csv')
    if len(df.index) > 0:
        return int(df.tail(1)['meeting_no'])
    else:
        return 0

def getLatestMeetingInfo():
    html = urlopen('https://www.bousai.metro.tokyo.lg.jp/taisaku/saigai/1013388/index.html')
    bsObj = BeautifulSoup(html, 'html.parser')
    ul = bsObj.select_one('ul.listlink')
    li = ul.select_one('li')
    url = 'https://www.bousai.metro.tokyo.lg.jp/' + li.select_one('a').get('href').replace('../../../', '')
    title = li.select_one('a').text
    no = int(re.search(r'第(\d+?)回', title).group(1))
    date = re.search(r'令和(\d+?)年(\d+?)月(\d+?)日', title)
    y = 2018 + int(date.group(1))
    m = int(date.group(2))
    d = int(date.group(3))
    date = '{0:%Y-%m-%d}'.format(datetime.date(y,m,d))
    return no, date, url

def getCommentPdfUrl(meeting_url):
    html = urlopen(meeting_url)
    bsObj = BeautifulSoup(html, 'html.parser')
    ul = bsObj.select_one('ul.objectlink')
    lis = ul.select('li')
    for li in lis:
        a = li.select_one('a')
        title = a.text
        if '専門家によるモニタリングコメント・意見' in title:
            url = 'https://www.bousai.metro.tokyo.lg.jp/' + a.get('href').replace('../../../', '')
            return url


def getPdfDataFrame(pdf_url):
    df = tabula.read_pdf(pdf_url, lattice=True, pages='all')
    df = pd.concat(df, ignore_index=True)
    df.columns = ['monitoring_index', 'graph', 'monitoring_comment']
    df['monitoring_comment']=df['monitoring_comment'].fillna(df['graph']) 
    df = df.drop('graph', axis=1)
    df['monitoring_index']=df['monitoring_index'].replace(r'[\r\n]','', regex=True)
    df['monitoring_comment']=df['monitoring_comment'].replace(r'[\r\n]','', regex=True)
    df['monitoring_index']=df['monitoring_index'].fillna(method='ffill')
    df['monitoring_index']=df['monitoring_index'].apply(lambda x: str(x)[0])
    df = df[df['monitoring_index'] != 'n']
    df = df.groupby('monitoring_index')['monitoring_comment'].apply(''.join).reset_index()
    return df

def splitComment(df):
    df_split = pd.DataFrame(index=[], columns=['meeting_no', 'meeting_date', 'monitoring_index', 'line_number', 'monitoring_comment'])
    for row in df.itertuples(name=None):
        meeting_no = row[1]
        meeting_date = row[2]
        monitoring_index = row[3]
        monitoring_comment = row[4]
        splits = monitoring_comment.split('。')
        splits.pop()
        for i in range(len(splits)):
            df_split.loc[len(df_split.index)] =  [meeting_no, meeting_date, monitoring_index, i + 1, splits[i] + '。']
    return df_split

def generateToken(df):
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
    df_token = df_token.replace('*', np.nan)
    return df_token

def main():
    last_meeting_no = getLastMeetingNo()
    meeting_no, meeting_date, meeting_url = getLatestMeetingInfo()
    if meeting_no > last_meeting_no:
        comment_pdf_url = getCommentPdfUrl(meeting_url)
        df = getPdfDataFrame(comment_pdf_url)
        df['meeting_no'] = meeting_no
        df['meeting_date'] = meeting_date

        df = df[['meeting_no', 'meeting_date', 'monitoring_index', 'monitoring_comment']]
        df.to_csv('data/monitoring_comments.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
        df_split = splitComment(df)
        df_split.to_csv('data/monitoring_comments_split.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
        df_token = generateToken(df_split)
        df_token.to_csv('data/monitoring_comments_token.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        print('error')
        print('meeting_no = ', meeting_no)
        print('last_meeting_no = ', last_meeting_no)
        sys.exit(1)

if __name__ == '__main__':
    main()