import requests
import bs4
from time import sleep
import pandas as pd
from google.colab import files
import re

# 検索したいキーワードを入力する
listKeyword = ['python', 'スクレイピング']

#　取得したい件数に合わせて数値を変更する
searchNum = str(10)

response = requests.get('https://www.google.co.jp/search?num='+searchNum+'&q=' + '　'.join(listKeyword))
response.raise_for_status()

# 取得したHTMLをパースする
soup = bs4.BeautifulSoup(response.content, "html.parser")

file_prefix = ""
for word in listKeyword:
  if (file_prefix == ""):
    file_prefix += str(word)
  else:
    file_prefix += "-" + str(word)

fileName = file_prefix+'_Top'+searchNum+'.csv'

# csvファイルのヘッダーを設定する
df = pd.DataFrame(columns=['URL','タイトル','ディスクリプション','キーワード'])

sleepCounter = 0

# 検索結果上位サイトのURLを取得する
for a in soup.select('div#search h3.r a'):
  sleepCounter += 1
  url = re.sub(r'/url\?q=|&sa.*', '',a.get('href'))

  try:
    # 取得したURLを読み込む
    search = requests.get(url)
    searchSoup = bs4.BeautifulSoup(search.content, "html.parser")

    # タイトルの取得
    titleList = []
    for a in searchSoup.select('title'):
      titleList.append(a.text)
    title=''

    for index,item in enumerate(titleList):
      if index==0:
        title = item
      else:
        title = title + ', ' +item

    # ディスクリプションの取得
    descriptionList = []
    for a in searchSoup.select('meta[name="description"]'):
      descriptionList.append(a.get('content'))
    description='No data'

    for index,item in enumerate(descriptionList):
      if index==0:
        description = item
      else:
        description = description + ', ' +item

    # キーワードの取得
    keywordList = []
    for a in searchSoup.select('meta[name="keywords"]'):
      keywordList.append(a.get('content'))
    keywords = 'No data'

    for index,item in enumerate(keywordList):
      if index==0:
        keywords = item
      else:
        keywords = keyword + ', ' +item

  except: #例外処理：サイトを読み込めなかったときにする処理
    print('Failed to read web site.')

  # 取得したURL、タイトル、ディスクリプション、キーワードを追加する
  outputRow = [url,title,description,keywords]
  s = pd.Series(outputRow, index=['URL','タイトル','ディスクリプション','キーワード'])
  df = df.append(s, ignore_index=True)

  # 10件以上検索する場合、秒間リクエスト数の制限を守るため、10件ごとに10秒の待機時間を設ける
  if sleepCounter > 10:
    sleep(10)
    sleepCounter = 0

# csvに出力する
df.to_csv(fileName, index=False)

# csvをダウンロードする
files.download(fileName)
