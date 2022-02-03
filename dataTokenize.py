# 使用CKIP套件對黨產會文本進行斷詞
# 建議在gpu環境下運作
# 2022/02/02 蘇彥庭
# CKIP套件程式碼範例: https://github.com/ckiplab/ckip-transformers
# CKIP套件安裝: pip install -U ckip-transformers
import pandas as pd
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker

# 讀取資料
data = pd.read_csv('./data/cipasCombineData.csv')

# 將缺值資料NaN改為空白格 避免CKIP遇到NaN文章報錯
data.loc[data['articleContent'].isna(), ['articleContent']] = ''

# 欲斷詞的文章資料
doc = data['articleContent'].tolist()

# 執行CKIP斷詞
ws_driver = CkipWordSegmenter(level=3, device=-1)  # use cpu
# ws_driver = CkipWordSegmenter(level=3, device=0)  # use gpu
ws = ws_driver(doc, use_delim=True)

# 整理斷詞後文章結果
output = []
for word_ws in ws:
    output.append('  '.join(word_ws))

# 儲存斷詞後文章結果
data['tokenize'] = output

# 輸出檔案
data.to_csv('./data/webTokenizeData.csv', index=False, encoding='utf-8-sig')