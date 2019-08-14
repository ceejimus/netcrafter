import re
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from .parsers import parse

NETCRAFT_TOOLBAR_URL='https://toolbar.netcraft.com/site_report'

def read_html_file(report_html_path: str) -> str:
    path = Path(report_html_path)
    with open(path.expanduser(), 'r') as f:
        return f.read()


def child_info_to_str(c: object) -> str:
    c_text = c
    c_type = type(c)
    if c_type is NavigableString:
        c_text = c.string
    return f'val: {c_text}|type: {str(c_type)}'

def is_empty_text(c: Tag) -> str:
    return type(c) is NavigableString and re.sub(r'\w+', '', c.string)

def get_tag_type(t: Tag) -> str:
    children = [c for c in t.children]
    if len(children) == 1 and type(children[0]) is NavigableString:
        return t.string

    if len(children) > 1:
        non_empty_children = [c for c in children if not is_empty_text(c)]
        # if len(non_empty_children) == 1 and type(non_empty_children[0]) is 
        print(f'when parsing found non-empty children: {",".join([child_info_to_str(c) for c in non_empty_children])}')
    debug = ",".join([child_info_to_str(c) for c in t.children])
    print(f'could not determine tag type for {t}\nchildren => {debug}')

def parse_section(section: Tag):
    # print(f'parsing "{section_title}"')
    section_title, section_info = parse(section)
    # section_info = get_parser(section_title)(section_table)
    # section_info = parse_table(section_title, section_table)
    return section_title, section_info

def soupify_report(html: str):
    info = {}
    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.find_all('section')
    for section in sections[0:3]:
        section_title, section_info = parse_section(section)
        info[section_title] = section_info
    return info


def netcraft(report_html_path: str):
    html = read_html_file(report_html_path)
    info = soupify_report(html)
    print(info)

if __name__ == '__main__':
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('report_html_path', help='Path to domain report HTML file.', type=str)
    # args = parser.parse_args()
    # netcraft(args.report_html_path)
    netcraft("~/Documents/Site report for www.bulbsecurity.com.html")

