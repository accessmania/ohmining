
import re



def _run(ppattern,pstring):

    pattern = re.compile(ppattern, re.I | re.MULTILINE)

    matched = pattern.finditer(pstring)

    result = []
    cursor = 0
    cursor_x = None
    cursor_y = None

    # --------------------------------------------------------
    match1 = re.search(ppattern, pstring)

    if match1: #첫번째 결과 누락을 방지하기 위함도 있음

        for r in matched:

            if cursor ==0 and cursor == r.span()[0]:

                #처음부터 키영역으로 시작하는 경우
                contents = {}

            elif cursor ==0 and cursor < r.span()[0]:

                #처음 , 키영역이 아닌 앞자리 짜투리
                contents = {}
                contents['key'] = None
                contents['key_xy'] = None
                contents['value'] = pstring[cursor: r.span()[0]]
                contents['value_xy'] = (cursor, r.span()[0])
                result.append(contents)
                contents = {}

            elif cursor < r.span()[0] :

                contents['value'] = pstring[cursor: r.span()[0]]
                contents['value_xy'] = (cursor, r.span()[0])
                result.append(contents)
                contents = {}

            elif cursor == r.span()[0] :

                contents['value'] = None
                contents['value_xy'] = (cursor, cursor)
                result.append(contents)
                contents = {}



            #key 영역저장

            contents['key'] = r.group()
            contents['key_xy'] = r.span()
            cursor = r.span()[1]

        # ---------------------------------------------------------------------------

        if len(pstring) > cursor:

            contents['value'] = pstring[cursor:]
            contents['value_xy'] = (cursor, len(pstring))
            result.append(contents)


        return result

    else:

        return []

def test ( ppattern , pstring):

    m = _run(ppattern, pstring)

    for i in m:

        if i['key'] != None and i['value'] != None:
            print("(k)" + i['key'] + " (v)" + i['value'])

        if i['key'] == None and i['value'] != None:
            print("(k)없음" + " (v)" + i['value'])

        if i['key'] != None and i['value'] == None:
            print("(k)" + i['key'] + "(v)없음")
