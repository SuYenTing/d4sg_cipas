# 不當黨產委員會PDF檔案下載與文字擷取
# 2022/01/23 蘇彥庭
import pandas as pd
import requests
import pdfplumber
import os
from tqdm import tqdm

# PDF檔案下載函數
def DownloadPdfFile(url, saveFileName):
    saveFileName = url.split('/')[-1]
    response = requests.get(url)
    with open(f'./data/pdf/{saveFileName}', 'wb') as f:
        f.write(response.content)


# 建立儲存資料夾
if 'pdf' not in os.listdir('./data'): os.mkdir('./data/pdf')

# 讀取黨產會提供文本資料檔案
rawData = pd.read_excel('./data/1101001-結構化資料體系-done.xlsx', header=[0, 1])
# 發現網址中的cipas改為cipas-production 其pdf的內容是相同的 且改為後的好處為可以和爬蟲資料做對應
rawData.iloc[:, 1] = rawData.iloc[:, 1].str.replace('/cipas/', '/cipas-production/')
# 取出連結欄位並過濾重複值
rawDataUrls = pd.unique(rawData.iloc[:, 1])
# 取出pdf結尾的連結
rawDataUrls = [elem for elem in rawDataUrls if elem.split('.')[-1] == 'pdf']
# 黨產會提供的資訊共有10筆資料

# 讀取黨產會官網附錄PDF檔案連結資訊
webAttachData = pd.read_csv('./data/cipasWebAttachData.csv')
webAttachData['fileType'] = webAttachData['attachFileLinks'].str.split('.', expand=True)[3]
webAttachData = webAttachData[webAttachData['fileType'] == 'pdf']

# 讀取政黨不動產查詢系統的附錄PDF檔案連結資訊
padAttachData = pd.read_csv('./data/cipasPadAttachData.csv')
padAttachData = padAttachData.drop(columns=['attachFileTypes'])
padAttachData['fileType'] = padAttachData['attachFileLinks'].str.split('.', expand=True)[3]
padAttachData = padAttachData[padAttachData['fileType'] == 'pdf']

# 合併資料 整理PDF檔案資料
pdfData = pd.concat([webAttachData, padAttachData])
pdfData = pdfData.drop(columns=['fileType'])
# 標記黨產會提供的pdf檔案連結
pdfData['mark'] = ['Y' if elem in rawDataUrls else 'N' for elem in pdfData['attachFileLinks']]

# 下載PDF資料
# 共有兩個雲端空間資料來源:
# 1. https://storage.googleapis.com/
# 2. https://dl8i3q8ook5lg.cloudfront.net/
pdfFileNameList = list()
for url in tqdm(pdfData['attachFileLinks']):
    # 儲存檔案名稱 
    saveFileName = url.split('/')[-1]
    # 判斷檔案是否已下載過 節省傳輸
    if saveFileName not in os.listdir('./data/pdf'):
        DownloadPdfFile(url, saveFileName)
    # 紀錄PDF檔案名稱
    pdfFileNameList.append(saveFileName)

# 將PDF檔案名稱新增進PDF檔案資料
pdfData['pdfFileNames'] = pdfFileNameList

# 迴圈讀取PDF檔案並擷取出文字
pdfFiles = os.listdir('./data/pdf/')
pdfContents = []
for pdfFile in tqdm(pdfFiles):
    pdf = pdfplumber.open(f'./data/pdf/{pdfFile}')
    pdfContent = '\n'.join([elem.extract_text() for elem in pdf.pages])
    pdfContents.append(pdfContent)

# 將將PDF檔案擷取文字新增進PDF檔案資料
pdfData['content'] = pdfContents

# 輸出PDF檔案資料
pdfData.to_csv('./data/pdfData.csv', encoding='utf-8-sig', index=False)
