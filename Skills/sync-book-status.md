# 技能：同步書籍狀態

> 隸屬於 [[CLAUDE]] · [[Skills/instructions|Skills 說明]]

## 觸發時機

- 使用者說「更新 XXX 的狀態」或「XXX 標成已讀」
- 使用者說「同步書籍狀態」（全部書同步）
- 任何修改書籍閱讀狀態或閱讀日期後

## 說明

書籍狀態存在兩個地方：
- **YAML frontmatter**（source of truth，Properties 面板編輯）
- **Blockquote**（文件內視覺顯示）

以 YAML 為準，同步更新 blockquote。

## 單本更新步驟

1. 修改目標書檔的 YAML frontmatter（狀態、閱讀日期）
2. 執行下方腳本（指定檔名）或執行全書同步

## 執行腳本

```python
import os, re

def sync_book(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return False

    _, fm, rest = content.split("---", 2)

    status_match = re.search(r'^狀態:\s*(.*)$', fm, re.MULTILINE)
    date_match = re.search(r'^閱讀日期:\s*(.*)$', fm, re.MULTILINE)
    status = status_match.group(1).strip() if status_match else ""
    date = date_match.group(1).strip() if date_match else ""

    # 更新 blockquote 中的狀態與日期
    rest = re.sub(r'^> 狀態：.*$', f'> 狀態：{status}', rest, flags=re.MULTILINE)
    rest = re.sub(r'^> 閱讀日期：.*$', f'> 閱讀日期：{date}', rest, flags=re.MULTILINE)

    new_content = f"---{fm}---{rest}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True

# 同步全部書

vault = "/mnt/c/Users/崇瑋/Documents/Obsidian Vault/圖書館"
exclude = {"instructions.md", "大綱.md", "演化學.md"}
for f in os.listdir(vault):
    if f.endswith(".md") and f not in exclude:
        sync_book(os.path.join(vault, f))
```
