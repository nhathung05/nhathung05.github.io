# -*- coding: utf-8 -*-
import requests, re, json
from six.moves import urllib_parse, html_parser
from addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE

def getdata(url):
    url = urllib_parse.unquote_plus(url)
    id_sheet = re.search(r"/d\/([a-zA-Z0-9-_]+)",url).group(1)
    if "gid" in url:
        gid = re.search(r"gid=(\d.*)",url).group(1)
    else:gid=0
    url = "https://docs.google.com/spreadsheets/d/" + id_sheet + "/gviz/tq?gid=" + str(gid) + "&headers=1"
    header = {'User-Agent': 'Vietmediaf /Kodi1.1.99-092019'}
    r = requests.get(url,headers=header,verify=False)
    nd = re.search(r'\((.*?)}\)', r.text).group(1) + '}'
    nd = json.loads(nd)
    
    #first row
    items1 = []
    if nd["table"]["cols"]:
        name = ''
        link = ''
        thumb = ''
        info = ''
        fanart = ''
        genre = ''
        rating = ''

        # Xử lý phần name
        if len(nd["table"]["cols"]) > 0:
            name_data = nd["table"]["cols"][0]
            name = name_data.get("label", "")
            if "|" in name:
                name_parts = name.split("|")
                name = name_parts[0].replace("*", "").replace("@", "")
                link = name_parts[1] if len(name_parts) > 1 else ""

        # Xử lý phần link
        if len(nd["table"]["cols"]) > 1:
            link_data = nd["table"]["cols"][1]
            link = link_data.get("label", "")
            if "token" in link:
                link = re.search(r"(https.+?)\/\?token", link).group(1) if match else ""

        # Xử lý phần thumb
        if len(nd["table"]["cols"]) > 2:
            thumb = nd["table"]["cols"][2].get("label", "")

        # Xử lý phần info
        if len(nd["table"]["cols"]) > 3:
            info = nd["table"]["cols"][3].get("label", "")
            # Xử lý phần fanart
        if len(nd["table"]["cols"]) > 4:
            fanart = nd["table"]["cols"][4].get("label", "")
        #Xử lí phần thể loại
        if len(nd["table"]["cols"]) > 5:
            genre = nd["table"]["cols"][5].get("label", "")
        #Xử lí phần rating
        if len(nd["table"]["cols"]) > 6:
            rating = nd["table"]["cols"][6].get("label", "")
            
        playable = not (("folder" in link or "menu" in link or "docs.google.com" in link or "m3uhttp" in link) or \
                ("4share.vn" in link and "/d/" in link) or ("api.4share.vn" in link and "/d/" in link))
        # Tạo dictionary items1 nếu name không rỗng
        if name and any(substring in link for substring in ['http', 'udp', 'rtp', 'acestream']):
            items1 = [{
                'label': name,
                'is_playable': playable,
                'path': 'plugin://plugin.video.vietmediaF?action=play&url=%s' % link,
                'thumbnail': thumb,
                'icon': thumb,
                'label2': '',
                'info': {
                    'plot': info,
                    'genre': genre,
                    'rating': rating
                },
                'art': {
                    "fanart": fanart,
                    "poster": thumb,
                    "thumb": thumb
                }
            }]
        else:
            items1 = []
    
    js = nd["table"]["rows"]
    items = []

    for link in js:
        item = {}
        row = link["c"]
        try:
            name = row[0]["v"].replace("||", "|")
        except Exception as e:
            #alert(f'Lỗi: {link}\n{str(e)}')
            name = 'Lỗi tên'

        if "|" in name:
            lis = name.split("|")
            name = lis[0].replace("*", "").replace("@", "")
            link = lis[1] if len(lis) > 1 else ""
            thumb = lis[2] if len(lis) > 2 else ""
            info = lis[3] if len(lis) > 3 else ""
            fanart = lis[4] if len(lis) > 4 else ""
        else:
            try:
                link = row[1]["v"]
                if "token" in link:
                    regex = r"(https.+?)\/\?token"
                    match = re.search(regex, link)
                    if match:
                        link = match.group(1)
            except:
                link = ""
            try:
                thumb = row[2]["v"]
            except:
                thumb = ""
            try:
                info = row[3]["v"]
            except:
                info = ""
            try:
                fanart = row[4]["v"]
            except:
                fanart = thumb
            try:
                genre = row[5]["v"]
            except:
                genre = ""
            try:
                rating = row[6]["v"]
            except:
                rating = ""

        playable = not (("folder" in link or "docs.google.com" in link or "pastebin.com" in link or "m3uhttp" in link or "menu" in link) or ("4share.vn" in link and "/d/" in link) or ("api.4share.vn" in link and "/d/" in link))

        if "item_driveid=" in link:
            # Trích xuất drive_id và item_id từ link OneDrive
            drive_id_match = re.search(r"item_driveid=([^&]+)", link)
            item_id_match = re.search(r"item_id=([^&]+)", link)

            if drive_id_match and item_id_match:
                drive_id = drive_id_match.group(1)
                item_id = item_id_match.group(1)
                onedrive_link = f'plugin://plugin.onedrive/?content_type=video&item_driveid={drive_id}&item_id={item_id}&driveid={drive_id}&action=play'

                item["label"] = f"{name} (OneDrive)"
                item["is_playable"] = True
                item["path"] = onedrive_link
                item["thumbnail"] = thumb
                item["icon"] = thumb
                item["label2"] = ""
                item["info"] = {'plot': info, 'genre': genre, 'rating': rating}
                item["art"] = {
                    "fanart": fanart,
                    "poster": thumb,
                    "thumb": thumb
                }

                items.append(item)

        elif any(substring in link for substring in ["http", "rtp", "udp", "acestream", "plugin"]):
            item["label"] = name if link else name + " - no link"
            item["is_playable"] = playable
            item["path"] = 'plugin://plugin.video.vietmediaF?action=play&url=%s' % link
            item["thumbnail"] = thumb
            item["icon"] = thumb
            item["label2"] = ""
            item["info"] = {'plot': info, 'genre': genre, 'rating': rating}
            item["art"] = {
                "fanart": fanart,
                "poster": thumb,
                "thumb": thumb
            }

            items.append(item)

    data = {"content_type": "movies", "items": items}
    #vDialog.close()
    
    return data