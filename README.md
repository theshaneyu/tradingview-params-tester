### 使用方式

1. 在 `config.json` 中設定每個參數的初值、上限以及每次迭代的增加量，並執行 `crawler.py` 即可
2. 執行 `crawler.py` 需要兩個系統參數：**帳號**和**合約**。執行範例：

```bash
python crawler.py shane nq
```

### Production 正式執行 checklist

**.env**

- `SEND_EAMIL` 是否打開
- `PTTHON_ENV` 是否為 prod

**config.json**

- `period` 參數範圍是否正確

**TradingView UI**

- 側邊欄是否關閉
