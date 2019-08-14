from bs4.element import Tag, NavigableString

def parse_text_tag(t: Tag) -> str:
    unavailable = t.find('span', { 'class': 'unavailable' })
    if (unavailable):
        return unavailable.string
    return t.string.strip()

def parse_anchor_tag(a: Tag) -> str:
    # debug = [c for c in a.children]
    print(f'[DEBUG] {a}({type(a)}) __ {["|".join([str(c), str(type(c))]) for c in a.children]}')
    return {
        ','.join([c.string.strip() for c in a.children if type(c) is NavigableString]): a['href']
    }

def parse_ip_address_tag(ip: Tag) -> str:
    children = [c for c in ip.children]

    return {
        'text': children[0].string.strip(),
        'link': parse_anchor_tag([c for c in children[1]][1])
    }

def parse_text_with_link_tag(t: Tag) -> str:
    children = [c for c in t.children]

    return {
        'text': children[0].string.strip(),
        'link': parse_anchor_tag(children[1])
    }

def parse_risk_rating_tag(t: Tag) -> str:
    return {
        'rating': int(t.find('span', { 'class': 'risk_label' })['data-risk'])
    }

text_parser = {
    'header': parse_text_tag,
    'data': parse_text_tag
}

def link_parser(t):
    return parse_anchor_tag(t.find('a'))

data_link_parser = {
    'header': parse_text_tag,
    'data': link_parser
}

kv_parsers = {
    "Background": {
        "Site title": text_parser,
        "Date first seen": text_parser,
        "Site rank": data_link_parser,
        "Primary language": text_parser,
        "Description": text_parser,
        "Keywords": text_parser,
        "Netcraft Risk Rating": {
            'header': parse_text_with_link_tag,
            'data': parse_risk_rating_tag
        }
    },
    "Network": {
        "Site": data_link_parser,
        "Domain": data_link_parser,
        "IP address": {
            'header': parse_text_tag,
            'data': parse_ip_address_tag
        },
        "IPv6 address": text_parser,
        "Domain registrar": text_parser,
        "Organisation": text_parser,
        "Top Level Domain": text_parser,
        "Netblock Owner": data_link_parser,
        "Hosting country": data_link_parser,
        "Nameserver": text_parser,
        "DNS admin": text_parser,
        "Reverse DNS": text_parser,
        "Nameserver organisation": text_parser,
        "Hosting company": text_parser,
        "DNS Security Extensions": text_parser
    }
}

grid_parsers = {
    'Hosting History': {
        'Netblock owner': link_parser,
        'IP address': parse_text_tag,
        'OS': parse_text_tag,
        'Web server': parse_text_tag,
        'Last seen': parse_text_tag
    }
}

def parse_key_value_table(section_title: str, tbody: Tag):
    section_info = {}
    rows = tbody.find_all('tr')
    for r in rows:
        headers = r.find_all('th')
        datas = r.find_all('td')
        #TODO: remove this and handle
        if len(headers) != len(datas):
           raise Exception(f'MISMATCH HEADERS DATA')
        for i in range(len(headers)):
            h = headers[i]
            d = datas[i]
            header, parser = get_kv_parser(section_title, h, d)
            if not parser:
                print(f'no parser found for {h}')
            else:
                try:
                    section_info[header] = {
                        'header': parser['header'](h),
                        'data': parser['data'](d)
                    }
                except:
                    print(f'FAILED TO PARSE: {header}\ntd: {h}\ntd: {d}')
                    raise
    return section_info

def get_kv_parser(section_title: str, th: Tag, td: Tag):
    section_parsers = kv_parsers[section_title]
    matching_keys = [k for k in section_parsers.keys() if k in str(th)]

    if not matching_keys:
        return None, None

    lengths = [len(k) for k in matching_keys]
    key = matching_keys[lengths.index(max(lengths))]
    return key, section_parsers[key]

def parse_grid_table(section_title: str, tbody: Tag):
    parsers = grid_parsers[section_title]
    headers = list(parsers.keys())
    section_info = []
    for i,r in enumerate(tbody.find_all('tr')):
        row_info = {}
        for j,td in enumerate(r.find_all('td')):
            header = headers[j]
            row_info[header] = parsers[header](td)
        section_info.append(row_info)
    return section_info

def get_parser(section_title: str):
    if section_title in kv_parsers:
        return lambda tbody: parse_key_value_table(section_title, tbody)
    if section_title in grid_parsers:
        return lambda tbody: parse_grid_table(section_title, tbody)

def parse(section: Tag):
    section_title = section.find('div', { 'class': 'section_title' }).find('h2').string
    section_table = section.find('div', { 'class': 'section_content' }).find('tbody')
    return section_title, get_parser(section_title)(section_table)