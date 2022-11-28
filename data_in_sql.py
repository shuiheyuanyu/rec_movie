import pandas as pd
from sqlalchemy import create_engine
import re


engine = create_engine("mysql+pymysql://root:root@localhost:3306/movie_re?charset=utf8")

"""
Load Dataset from File
"""
# # 读取User数据
# users_title = ['UserID', 'Gender', 'Age', 'JobID', 'Zip-code']
# users = pd.read_table('./ml-1m/users.dat', sep='::', header=None, names=users_title, engine='python')
#
# JobID_map = {0:'other', 1:'academi', 2:'artist', 3:'clerical', 4:'college', 5:'customer service',
#              6:'doctor', 7:'executive', 8:'farmer', 9:'homemaker', 10:'student', 11:'lawyer', 12:'programmer',
#              13:'retired', 14:'sales', 15:'scientist', 16:'self-employed', 17:'technician', 18:'tradesman',
#              19:'unemployed', 20:'writer'}
#
# user_1 = pd.DataFrame(users,)
# user_1['JobID'] = user_1.JobID.map(JobID_map)
# #user_1.set_index('UserID',drop=True)
# user_1.rename(columns={'UserID':'id'},inplace=True)
# user_1['username'] = user_1['id'].apply(str)
# user_1['password'] = '111'
# user_1['email'] = '1212454@qq.com'
# user_1['power'] = 'user'


# # 读取Movie数据集
# movies_title = ['MovieID', 'Title', 'Genres']
# movies = pd.read_table('./ml-1m/movies.dat', sep='::', header=None, names=movies_title, engine='python')
# movies_orig = movies.values
# # 将Title中的年份去掉
# pattern = re.compile(r'^(.*)\((\d+)\)$')
#
# title_map = {val: pattern.match(val).group(1) for ii, val in enumerate(set(movies['Title']))}
# movies['Title'] = movies['Title'].map(title_map)
#
# # 电影类型转数字字典
# genres_set = set()
# for val in movies['Genres'].str.split('|'):
#     genres_set.update(val)
#
# genres_set.add('<PAD>')
# genres2int = {val: ii for ii, val in enumerate(genres_set)}
#
# # 将电影类型转成等长数字列表，长度是18
# genres_map = {val: [genres2int[row] for row in val.split('|')] for ii, val in enumerate(set(movies['Genres']))}
#
# for key in genres_map:
#     for cnt in range(max(genres2int.values()) - len(genres_map[key])):
#         genres_map[key].insert(len(genres_map[key]) + cnt, genres2int['<PAD>'])
#
# movies['Genres'] = movies['Genres'].map(genres_map)
#
# # 电影Title转数字字典
# title_set = set()
# for val in movies['Title'].str.split():
#     title_set.update(val)
#
# title_set.add('<PAD>')
# title2int = {val: ii for ii, val in enumerate(title_set)}
#
# # 将电影Title转成等长数字列表，长度是15
# title_count = 15
# title_map = {val: [title2int[row] for row in val.split()] for ii, val in enumerate(set(movies['Title']))}
#
# for key in title_map:
#     for cnt in range(title_count - len(title_map[key])):
#         title_map[key].insert(len(title_map[key]) + cnt, title2int['<PAD>'])
#
# movies['Title'] = movies['Title'].map(title_map)

# 读取评分数据集
ratings_title = ['UserID', 'MovieID', 'ratings', 'timestamps']
ratings = pd.read_table('./ml-1m/ratings.dat', sep='::', header=None, names=ratings_title, engine='python')
ratings = ratings.filter(regex='UserID|MovieID|ratings')

#
# print(user_1.head)
# user_1.to_sql("user", engine, schema="movie_re", if_exists='replace', index=False,
#             chunksize=None, dtype=None)
print(ratings.head)
ratings.to_sql("ratings", engine, schema="movie_re", if_exists='replace', index=False,
             chunksize=None, dtype=None)