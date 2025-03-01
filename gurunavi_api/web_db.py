import json
import sys
import urllib.parse
import urllib.request
import dataset
from bottle import route, run, request

db = dataset.connect('mysql://roots:rootroot@127.0.0.1:3311/mysql')
table = db['ra-men']
keyid = "fdbe93860953f0d14f763117f55b38ab"


@route('/')
def normal_page():
    return 'wa-i'


def get_freeword(user_id):
    s_data = table.find_one(id=user_id)
    freeword = s_data['name']
    return freeword


def get_gurunavi(freeword):
    query = {"format", "json",
             "keyid", keyid,
             "freeword", freeword,
             "freeword_condition", '2'
             }
    url = "https://api.gnavi.co.jp/RestSearchAPI/20150630/"
    # API実行
    try:
        result = request.get(url, query)
        return result.json()
    except ValueError:
        print(u"APIアクセスに失敗しました。")
        sys.exit()


def search_rest(json_data):
    # レストランデータ取得
    disp_count = 0
    line = []
    for rest in json_data["rest"]:
        if "name" in rest:
            name = u"{0}".format(rest["name"])
            line.append(name)
        if "latitude" in rest:
            latitude = u"{0}".format(rest["latitude"])
            line.append(latitude)
        if "longitude" in rest:
            longitude = u"{0}".format(rest["longitude"])
            line.append(longitude)
        if "category" in rest:
            category = u"{0}".format(rest["category"])
            line.append(category)
        if "url" in rest:
            url = u"{0}".format(rest["url"])
            line.append(url)
        if "address" in rest:
            address = u"{0}".format(rest["address"])
            line.append(address)
        print("\t".join(line))
        disp_count += 1
    return line


@route('/<user_id>', method="get")
def modify_item(user_id):
    s_data = table.find_one(id=user_id)
    freeword = s_data['name']
    query = [
        ("format", "json"),
        ("keyid", keyid),
        ("freeword", freeword),
        ("freeword_condition", '2')
    ]
    url = "https://api.gnavi.co.jp/RestSearchAPI/20150630/"
    # URL生成
    url += "?{0}".format(urllib.parse.urlencode(query))
    # API実行
    try:
        result = urllib.request.urlopen(url).read()
        data = json.loads(result)
        print("繋がっている")
    except ValueError:
        print(u"APIアクセスに失敗しました。")
        sys.exit()

    # エラーの場合
    if "error" in data:
        if "message" in data:
            print(u"{0}".format(data["message"]))
        else:
            print(u"データ取得に失敗しました。")
        sys.exit()

    # ヒット件数取得
    total_hit_count = None
    if "total_hit_count" in data:
        total_hit_count = data["total_hit_count"]

    # レストランデータがなかったら終了
    if not "rest" in data:
        print(u"レストランデータが見つからなかったため終了します。")
        sys.exit()

    # 出力件数
    disp_count = 0
    dict = []
    # レストランデータ取得
    for rest in data["rest"]:
        line = []
        if "name" in rest:
            name = u"{0}".format(rest["name"])
            line.append(name)
        if "latitude" in rest:
            latitude = u"{0}".format(rest["latitude"])
            line.append(latitude)
        if "longitude" in rest:
            longitude = u"{0}".format(rest["longitude"])
            line.append(longitude)
        if "category" in rest:
            category = u"{0}".format(rest["category"])
            line.append(category)
        if "url" in rest:
            url = u"{0}".format(rest["url"])
            line.append(url)
        if "url" in rest:
            address = u"{0}".format(rest["address"])
            line.append(address)
        print("\t".join(line))
        dict.append(line)
        disp_count += 1

    # 出力件数を表示して終了
    print("----")
    print(u"{0}件出力しました。".format(disp_count))

    print(dict)
    return data


@route('/', method="post")
def post_page():
    json = request.json
    id = str(json['id'])
    name = json['name']
    table.insert(dict(id=id, name=name))
    # return id + "の" + name + 'さんを追加しました'


@route('/<user_id>', method="delete")
def delete_page(user_id):
    result = table.find_one(id=user_id)
    id = str(result['id'])
    name = result['name']
    table.delete(id=user_id)
    return id + "の" + name + 'さんを削除しました'


@route('/<user_id>', method="put")
def put_page(user_id):
    json = request.json
    id = str(json['id'])
    name = json['name']
    data = dict(id=id, name=name)
    table.upsert(data, ['id'])
    return id + "の" + name + 'の名前を変更しました'


if __name__ == '__main__':
    run(host='localhost', port=3309)
