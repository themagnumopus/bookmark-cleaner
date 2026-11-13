import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

st.title("Bookmark Cleaner")
st.write("Upload your bookmark exports (Chrome/Brave HTML or Raindrop CSV). Get one clean file back.")

files = st.file_uploader("Upload files", type=["html", "csv"], accept_multiple_files=True)


def read_html(file):
    soup = BeautifulSoup(file, "html.parser")
    rows = []
    for link in soup.find_all("a"):
        rows.append({
            "title": link.get_text(),
            "url": link.get("href"),
            "added": link.get("add_date"),
        })
    table = pd.DataFrame(rows)
    table["added"] = pd.to_datetime(pd.to_numeric(table["added"], errors="coerce"), unit="s")
    table["source"] = file.name
    return table


def read_csv(file):
    table = pd.read_csv(file)
    table = table.rename(columns={"created": "added"})
    table["added"] = pd.to_datetime(table["added"], errors="coerce", utc=True).dt.tz_localize(None)
    table["source"] = file.name
    return table


if files:
    tables = []
    for file in files:
        if file.name.endswith(".html"):
            tables.append(read_html(file))
        else:
            tables.append(read_csv(file))

    all_bm = pd.concat(tables, ignore_index=True)
    before = len(all_bm)
    all_bm = all_bm.drop_duplicates(subset="url")
    all_bm = all_bm.reindex(columns=["title", "url", "added", "folder", "tags", "note", "source"])

    st.success(f"{before} bookmarks found, {before - len(all_bm)} duplicates removed.")

    query = st.text_input("Search your bookmarks")
    if query:
        match = all_bm["title"].str.contains(query, case=False, na=False) | \
                all_bm["url"].str.contains(query, case=False, na=False)
        st.dataframe(all_bm[match])
    else:
        st.dataframe(all_bm)

    st.download_button("Download clean CSV", all_bm.to_csv(index=False), "clean_bookmarks.csv")