import re
from bs4 import BeautifulSoup

def escape_javascript(html_document):



    html_doc = BeautifulSoup(html_document , "html.parser").prettify()
    html_doc = re.sub("<(s|S)(c|C)(r|R)(i|I)(p|P)(t|T)" , "&lt;script",html_doc)
    html_doc = re.sub("</(s|S)(c|C)(r|R)(i|I)(p|P)(t|T)>" , "&lt;/script&gt;" , html_doc)
    html_doc = re.sub("(j|J)(a|A)(v|V)(a|A)(s|S)(c|C)(r|R)(i|I)(p|P)(t|T):" , "javascript:",html_doc)
    html_doc = re.sub("<.*\son.*=(\"|').*>" , "", html_doc)

    return html_doc
