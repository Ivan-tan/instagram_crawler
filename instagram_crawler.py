import requests
import pandas as pd
import datetime
import sys

def crawl(alias, limit, dir_save):
    base_url = "https://www.instagram.com/%s/?__a=1" % alias
    url = base_url

    count = 0
    all_dfs = []
    r = requests.get(base_url)
    if r.json()["graphql"]["user"]["is_private"]:
        print("%s is a private account!" % alias)
        return None
    followers = r.json()["graphql"]["user"]["edge_followed_by"]["count"]
    while count <= limit:
        if r.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]:
            max_id = r.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
            url = "%s&max_id%s" % (base_url, max_id)
            r = requests.get(url)
            posts = r.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
            dfs = [pd.DataFrame(a).transpose().reset_index(drop=True) for a in posts]
            all_dfs.extend(dfs)
            count += len(dfs)

    concat_df = pd.concat(all_dfs).reset_index(drop=True)
    concat_df["followers"] = followers
    concat_df["caption"] = concat_df.edge_media_to_caption.apply(lambda x: x["edges"][0]["node"]["text"])
    concat_df["timestamp"] = pd.to_datetime(concat_df.taken_at_timestamp, unit="s")
    concat_df["likes"] = concat_df.edge_liked_by.apply(lambda x: x["count"])
    concat_df["comments"] = concat_df.edge_media_to_comment.apply(lambda x: x["count"])

    clean_df = concat_df[["timestamp", "is_video", "caption", "display_url", "likes", "comments", "followers"]]

    clean_df.to_csv(dir_save+"/"+alias+".csv", index=False)

def main():
    alias = sys.argv[1]
    try:
        limit = sys.argv[2]
    except IndexError:
        limit = 100
    print("Extracting first %s posts for %s" % (limit, alias))
    dir_save = "./"
    crawl(alias, limit, dir_save)

if __name__ == "__main__":
    main()
