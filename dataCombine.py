# 依黨產會提供之文本連結檔案整併文章及附檔文字資料
# 2022/02/01 蘇彥庭
import pandas as pd
import sys

# 讀取資料
rawData = pd.read_excel('./data/1101001-結構化資料體系-done.xlsx', header=[0, 1])
cipasData = pd.read_excel('./data/1101001-結構化資料體系-done.xlsx')
cipasPadAttachData = pd.read_csv('./data/cipasPadAttachData.csv')
cipasPadContentData = pd.read_csv('./data/cipasPadContentData.csv')
cipasWebAttachData = pd.read_csv('./data/cipasWebAttachData.csv')
cipasWebContentData = pd.read_csv('./data/cipasWebContentData.csv')
pdfData = pd.read_csv('./data/pdfData.csv')

# 取出附檔為pdf格式
cipasPadAttachData = cipasPadAttachData[cipasPadAttachData['attachFileNames'].str.contains('pdf')]
cipasWebAttachData = cipasWebAttachData[cipasWebAttachData['attachFileNames'].str.contains('pdf')]

# 合併pdf文章內容至附件資料
cipasWebAttachData = cipasWebAttachData.merge(pdfData[['attachFileLinks', 'content']], on=['attachFileLinks'], how='left')
cipasPadAttachData = cipasPadAttachData.merge(pdfData[['attachFileLinks', 'content']], on=['attachFileLinks'], how='left')

# 建立輸出結果表
linkData = pd.DataFrame(data={'raw_url': rawData.iloc[:, 1]})
# 刪除重複資料
linkData = linkData.drop_duplicates()
# 建立調整後的url欄位
linkData['url'] = linkData['raw_url']
# 將連結中出現的cipas改為cipas-production方便對應
linkData['url'] = linkData['url'].str.replace('/cipas/', '/cipas-production/')
# 將連結中出現的gazettes改為news方便對應
linkData['url'] = linkData['url'].str.replace('/gazettes/', '/news/')

# 迴圈連結併入資料
output = pd.DataFrame()
# row = linkData.iloc[0]
for index, row in linkData.iterrows():
    
    # 若為純pdf連結 則直接取出該pdf檔案資訊
    if 'pdf' in row['url']:
        
        if len(pdfData[pdfData['attachFileLinks'] ==  row['url']]) != 1:
            sys.exit('該筆連結對應到的資料非1筆 請確認資料')
        iOutput = pdfData[pdfData['attachFileLinks'] ==  row['url']][['attachFileLinks', 'attachFileNames', 'content']]
        iOutput.columns = ['url', 'articleTitle', 'articleContent']
        iOutput.insert(1, 'type', 'main')

    # 若為新聞稿(公告)與史料故事連結
    elif any(elem in row['url'] for elem in ['news', 'stories']):

        if len(cipasWebContentData[cipasWebContentData['url'] ==  row['url']]) != 1:
            sys.exit('該筆連結對應到的資料非1筆 請確認資料')
        iData = cipasWebContentData[cipasWebContentData['url'] ==  row['url']]
        # 整理主文
        iOutput = iData[['url', 'articleTitle', 'articleContent']]
        iOutput.insert(1, 'type', 'main')
        # 整理附檔
        iAttachData = cipasWebAttachData[(cipasWebAttachData['source'] == iData['source'].tolist()[0]) & (cipasWebAttachData['id'] == iData['id'].tolist()[0])]
        iAttachData = iAttachData[['attachFileNames', 'content']]
        iAttachData.columns = ['articleTitle', 'articleContent']
        iAttachData.insert(0, 'url', iOutput['url'].tolist()[0])
        iAttachData.insert(1, 'type', 'attach')
        # 合併資料
        iOutput = pd.concat([iOutput, iAttachData])

    elif 'picks' in row['url']:

        if len(cipasPadContentData[cipasPadContentData['url'] ==  row['url']]) != 1:
            sys.exit('該筆連結對應到的資料非1筆 請確認資料')
        iData = cipasPadContentData[cipasPadContentData['url'] ==  row['url']]
        # 整理主文
        iOutput = iData[['url', 'articleTitle', 'articleContent']]
        iOutput.insert(1, 'type', 'main')
        # 整理附檔
        iAttachData = cipasPadAttachData[(cipasPadAttachData['source'] == iData['source'].tolist()[0]) & (cipasPadAttachData['id'] == iData['id'].tolist()[0])]
        iAttachData = iAttachData[['attachFileNames', 'content']]
        iAttachData.columns = ['articleTitle', 'articleContent']
        iAttachData.insert(0, 'url', iOutput['url'].tolist()[0])
        iAttachData.insert(1, 'type', 'attach')
        # 合併資料
        iOutput = pd.concat([iOutput, iAttachData])

    else:
        sys.exit('查無對應資料 請確認資料')

    # 合併資料
    iOutput.insert(0, 'raw_url', row['raw_url'])
    output = pd.concat([output, iOutput])


# 檢查`1101001-結構化資料體系-done.xlsx`內的檔案連結是否都已在合併資料內
for index, row in linkData.iterrows():
    if not any(output['raw_url'].isin(row[['raw_url']])):
        print('查詢無資料: ' + row['raw_url'])

# 輸出資料表
output.to_csv('./data/cipasCombineData.csv', index=False, encoding='utf-8-sig')