from bs4 import BeautifulSoup
import pandas as pd

with open("bookmarks.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

rows = []
for link in soup.find_all("a"):
    rows.append({
        "title": link.get_text(),
        "url": link.get("href"),
        "added": link.get("add_date"),
    })

df = pd.DataFrame(rows)
df["added"] = pd.to_datetime(pd.to_numeric(df["added"], errors="coerce"), unit="s")

print(df.shape)
print(df.head())

# ---- Lesson: how splitting works ----
url = "https://github.com/abc"
parts = url.split("/")
print(parts)
print(parts[2])

# ---- Top 10 websites you bookmark ----
df["domain"] = df["url"].str.split("/").str[2]
print(df["domain"].value_counts().head(10))

# ---- Raindrop bookmarks ----
rd = pd.read_csv("Rbookmarks.csv")
print(rd.shape)
print(rd.columns)

# ---- Merge Brave + Raindrop into one table ----
df["source"] = "brave"
rd["source"] = "raindrop"

rd = rd.rename(columns={"created": "added"})
rd["added"] = pd.to_datetime(rd["added"], errors="coerce", utc=True).dt.tz_localize(None)

all_bm = pd.concat([df, rd], ignore_index=True)
print(all_bm.shape)

all_bm = all_bm.drop_duplicates(subset="url")
print(all_bm.shape)

all_bm = all_bm[["title", "url", "added", "folder", "tags", "note", "source"]]
print(all_bm["source"].value_counts())

all_bm.to_csv("all_bookmarks.csv", index=False)