import pandas as pd

df = pd.read_csv("data/monitoring_comments.csv", header=None, skiprows=1, encoding="utf_8_sig")
df_steps = pd.DataFrame(index=[], columns=['meeting_no', 'meeting_date', 'monitoring_index', 'line_number', 'monitoring_comment'])
for row in df.itertuples(name=None):
    meeting_no = row[1]
    meeting_date = row[2]
    monitoring_index = row[3]
    monitoring_comment = row[4]
    steps = monitoring_comment.split('。')
    steps.pop()
    for i in range(len(steps)):
        df_steps.loc[len(df_steps.index)] =  [meeting_no, meeting_date, monitoring_index, i + 1, steps[i] + '。']
df_steps.to_csv('data/monitoring_comments_split.csv', index=False, encoding='utf-8-sig')