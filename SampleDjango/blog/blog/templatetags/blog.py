from django import template

register = template.Library()

# カスタムタグ
# GETにあるurlにキーを追加してそのキーに値を設定
# その後にurl文にして返す
@register.simple_tag
def replace(request, key, value):
    url_dict = request.GET.copy()
    url_dict[key] = value
    
    return url_dict.urlencode()