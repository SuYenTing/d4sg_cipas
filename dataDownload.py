# 不當黨產委員會文本資料下載
# 2022/01/22 蘇彥庭
# 文本來源類型
# 1. 首頁->公告資訊: https://www.cipas.gov.tw/gazettes/
# 2. 首頁->新聞: https://www.cipas.gov.tw/news/
# 3. 首頁->史料故事: https://www.cipas.gov.tw/stories/
# 4. 政黨不動產查詢系統: https://cipas-pad.nat.gov.tw/picks/
# 其中公告資訊, 新聞, 史料故事網站採用同一框架 可採用相同爬蟲程式碼
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm


# 下載黨產會官網公告資訊/新聞/史料故事
def DownloadCipasWeb(response):

    # 取得網頁內容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 文章標題
    articleTitle = soup.select('h1.page-header')[0].getText()
    # 文章發布日期
    articleDate = soup.select('div.date.small.text-muted')[0].getText()
    articleDate = articleDate.replace('發布日期：', '')
    # 文章內容
    articleContent = soup.select('div.article.row-w-limit')[0].getText()
    # 相關檔案連結
    attachFileLinks = [elem.get('href') for elem in soup.select('ul.attachfiles li a')]
    # 相關檔案名稱
    attachFileNames = [elem.getText().replace('檔案名稱：  ', '') for elem in soup.select('ul.attachfiles li a')]

    # 整理文章內容資料
    contentData = pd.DataFrame(data={
        'source': url.split('/')[-2],
        'id': url.split('/')[-1],
        'url': url,
        'articleTitle': articleTitle,
        'articleDate': articleDate,
        'articleContent': articleContent
        }, index=[0])

    # 整理附件資料
    attachData = pd.DataFrame(data={
        'source': url.split('/')[-2],
        'id': url.split('/')[-1],
        'attachFileNames': attachFileNames,
        'attachFileLinks': attachFileLinks,
        })

    return contentData, attachData
    

# 下載政黨不動產查詢系統文章
def DownloadCipasPad(response):

    # 轉換為soup格式
    soup = BeautifulSoup(response.text, 'html.parser')

    # 文章標題
    articleTitle = soup.select('h2.section-heading')[0].getText()
    # 文章內容
    articleContent = soup.select('section.feature-pick-article__story')[0].getText()
    # 相關檔案名稱
    attachFileNames = [elem.getText() for elem in soup.select('div.list-card ul.list li a.list__cell')]
    # 相關檔案連結
    attachFileLinks = [elem.get('href') for elem in soup.select('div.list-card ul.list li a.list__cell')]
    attachFileLinks = [f'https://cipas-pad.nat.gov.tw{elem}' if '/asset/' in elem else elem for elem in attachFileLinks]
    # 相關檔案類型
    attachFileTypes = ['關聯黨產' if '/asset/' in elem else '附檔' for elem in attachFileLinks]

    # 整理文章內容資料
    contentData = pd.DataFrame(data={
        'source': url.split('/')[-2],
        'id': url.split('/')[-1],
        'url': url,
        'articleTitle': articleTitle,
        'articleContent': articleContent
        }, index=[0])

    # 整理附件資料
    attachData = pd.DataFrame(data={
        'source': url.split('/')[-2],
        'id': url.split('/')[-1],
        'attachFileTypes': attachFileTypes,
        'attachFileNames': attachFileNames,
        'attachLinks': attachFileLinks,
        })

    return contentData, attachData


# 下載黨產會官網公告資訊/新聞/史料故事
cipasWebContentData = pd.DataFrame()
cipasWebAttachData = pd.DataFrame()
for source in ['gazettes', 'news', 'stories']:

    # 查詢失敗次數初始值: 若失敗次數超過上限則認為該資料來源已無資料可下載
    noPageNums = 0
    # 文章id初始值
    id = 1
    while noPageNums <= 10:

        print(f'目前正在下載資料來源: {source}  第 {id} 篇文章')

        # 下載資料
        url = f'https://www.cipas.gov.tw/{source}/{id}'
        response = requests.get(url, allow_redirects=False)
        if response.status_code == 200:
            contentData, attachData = DownloadCipasWeb(response)
            cipasWebContentData = pd.concat([cipasWebContentData, contentData])
            cipasWebAttachData = pd.concat([cipasWebAttachData, attachData])
            noPageNums = 0
        else:
            noPageNums += 1

        # 爬取下一頁
        id += 1
        time.sleep(1)

    print(f'{source} 已無新資料頁面 資料下載結束')

# 輸出結果
cipasWebContentData.to_csv('cipasWebContentData.csv', encoding='utf-8-sig', index=False)
cipasWebAttachData.to_csv('cipasWebAttachData.csv', encoding='utf-8-sig', index=False)


# 下載政黨不動產查詢系統文章
cipasPadContentData = pd.DataFrame()
cipasPadAttachData = pd.DataFrame()

# 查詢失敗次數初始值: 若失敗次數超過上限則認為該資料來源已無資料可下載
noPageNums = 0
# 文章id初始值
id = 1
while noPageNums <= 10:

    print(f'目前正在下載資料來源: picks  第 {id} 篇文章')

    # 下載資料
    url = f'https://cipas-pad.nat.gov.tw/picks/{id}'
    response = requests.get(url, allow_redirects=False)
    if response.status_code == 200:
        contentData, attachData = DownloadCipasPad(response)
        cipasPadContentData = pd.concat([cipasPadContentData, contentData])
        cipasPadAttachData = pd.concat([cipasPadAttachData, attachData])
        noPageNums = 0
    else:
        noPageNums += 1

    # 爬取下一頁
    id += 1
    time.sleep(1)

print('picks 已無新資料頁面 資料下載結束')

# 輸出結果
cipasPadContentData.to_csv('cipasPadContentData.csv', encoding='utf-8-sig', index=False)
cipasPadAttachData.to_csv('cipasPadAttachData.csv', encoding='utf-8-sig', index=False)
