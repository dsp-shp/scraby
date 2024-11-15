import typing as t
from enum import Enum, EnumType


class HTMLTag(Enum):
    """ Enumeration of HTML tags """
    ABBREVIATION = 'abbr'
    ACRONYM = 'acronym'
    ADDRESS = 'address'
    ANCHOR = 'a'
    APPLET = 'applet'
    AREA = 'area'
    ARTICLE = 'article'
    ASIDE = 'aside'
    AUDIO = 'audio'
    BASE = 'base'
    BASEFONT = 'basefont'
    BDI = 'bdi'
    BDO = 'bdo'
    BGSOUND = 'bgsound'
    BIG = 'big'
    BLOCKQUOTE = 'blockquote'
    BODY = 'body'
    BOLD = 'b'
    BREAK = 'br'
    BUTTON = 'button'
    CAPTION = 'caption'
    CANVAS = 'canvas'
    CENTER = 'center'
    CITE = 'cite'
    CODE = 'code'
    COLGROUP = 'colgroup'
    COLUMN = 'col'
    DATA = 'data'
    DATALIST = 'datalist'
    DD = 'dd'
    DEFINE = 'dfn'
    DELETE = 'del'
    DETAILS = 'details'
    DIALOG = 'dialog'
    DIR = 'dir'
    DIV = 'div'
    DL = 'dl'
    DT = 'dt'
    EMBED = 'embed'
    FIELDSET = 'fieldset'
    FIGCAPTION = 'figcaption'
    FIGURE = 'figure'
    FONT = 'font'
    FOOTER = 'footer'
    FORM = 'form'
    FRAME = 'frame'
    FRAMESET = 'frameset'
    HEAD = 'head'
    HEADER = 'header'
    HEADING1 = 'h1'
    HEADING2 = 'h2'
    HEADING3 = 'h3'
    HEADING4 = 'h4'
    HEADING5 = 'h5'
    HEADING6 = 'h6'
    HGROUP = 'hgroup'
    HR = 'hr'
    HTML = 'html'
    IFRAMES = 'iframe'
    IMAGE = 'img'
    INPUT = 'input'
    INS = 'ins'
    ISINDEX = 'isindex'
    ITALIC = 'i'
    KBD = 'kbd'
    KEYGEN = 'keygen'
    LABEL = 'label'
    LEGEND = 'legend'
    LIST = 'li'
    MAIN = 'main'
    MARK = 'mark'
    MARQUEE = 'marquee'
    MENUITEM = 'menuitem'
    META = 'meta'
    METER = 'meter'
    NAV = 'nav'
    NOBREAK = 'nobr'
    NOEMBED = 'noembed'
    NOSCRIPT = 'noscript'
    OBJECT = 'object'
    OPTGROUP = 'optgroup'
    OPTION = 'option'
    OUTPUT = 'output'
    PARAGRAPHS = 'p'
    PARAM = 'param'
    PHRASE = 'em'
    PRE = 'pre'
    PROGRESS = 'progress'
    Q = 'q'
    RP = 'rp'
    RT = 'rt'
    RUBY = 'ruby'
    S = 's'
    SAMP = 'samp'
    SCRIPT = 'script'
    SECTION = 'section'
    SMALL = 'small'
    SOURCE = 'source'
    SPACER = 'spacer'
    SPAN = 'span'
    STRIKE = 'strike'
    STRONG = 'strong'
    STYLE = 'tagname'
    SUMMARY = 'summary'
    SVG = 'svg'
    TABLE = 'table'
    TBODY = 'tbody'
    TD = 'td'
    TEMPLATE = 'template'
    TFOOT = 'tfoot'
    TH = 'th'
    THEAD = 'thead'
    TIME = 'time'
    TITLE = 'title'
    TR = 'tr'
    TRACK = 'track'
    TT = 'tt'
    UNDERLINE = 'u'
    VAR = 'var'
    VIDEO = 'video'
    WBR = 'wbr'
    XMP = 'xmp'

    @classmethod
    def values(cls) -> list[str]:
        return [x.value for x in cls]
