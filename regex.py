import re
import pandas as pd
import numpy as np
from datetime import datetime

      

class clsRegex :

    vpattern=None
    vstring =None

    def __init__(self , ppattern=None , pstring=None):

        self.vpattern = ppattern
        self.vstring = pstring

    def _regex_pattern_string (self ):

        result =[] 

        for forloop_pattern in self.vpattern:
            
            pattern = re.compile(forloop_pattern['pattern_keys'], re.I | re.MULTILINE)
            
            matched = pattern.finditer(self.vstring )

            for forloop in matched:
                
                ex_result ={}                
                
                for forloopkey in forloop_pattern:
                    ex_result[forloopkey] = forloop_pattern[forloopkey]
                    #좌표,문구 추출
                

                ex_result['context_words'] = bool(ex_result['context_words'])
                ex_result['context'] = None
                ex_result['span'] = forloop.span()
                ex_result['pre-match'] = None
                ex_result['match'] = forloop.group()
                ex_result['next-match'] = None
                ex_result['isduplication'] = False
                
                
                
                result.append (ex_result)


        return result



    #좌표가 겹치면 제거
    def _deduplication ( self , pxy1 , pxy2 ):

        '''
            중복정의
            x ~ y 에서  ( y2 < x or  y <= x2 ) 의 not 이 결과

        '''
        x = pxy1[0]
        y = pxy1[1]

        x2 = pxy2[0]
        y2 = pxy2[1]

        
        if ( y2 < x or y <= x2 ) == False :
            return True
        else :
            return False
        

    def _getRegexFirstWords ( self , ppattern , pstring):

        try:

            pattern = re.compile(ppattern, re.I | re.MULTILINE)
            matched = pattern.finditer(pstring)
            for forloop in matched:
                return forloop.group()

            return None
        except:
            print ('error')
            return None    

    def _nextIndex ( self , pcurrentIndex ,  presult , maxIndex ) :
        '''
            다음 노드를 찾는데 좌표가 겹치지 않는 다음 노드를 찾아 반환
        '''
        
        pcurrentIndex = pcurrentIndex +1

        for i in range ( pcurrentIndex  , maxIndex ):
            
            if presult[i]['isduplication'] == False:

                return i
            else:
                pass
                
        return maxIndex


    def _mergingResult(self , presult  ):

        cursor = 0
        maxindex = len ( presult ) -1
        nextX =None
        context =None
        nextIndex = None 

        for index , value in enumerate ( presult ):


            if bool(value['context_words']) == True :
                
                if value['key_values'] is not None and len( str(value['key_values']) ) > 0:
                    context = value['key_values']
                else:
                    context = value['match']

            else:
                ##################################################
                # bool(value['context_words']) == Frue 인경우만


                #중복체크제거
                if index + 1 <= maxindex :
                    
                    if self._deduplication(presult[index]['span'] ,presult[index +1]['span'] ) == True :
                        
                        presult[index +1]['isduplication'] = True # 이 경우



                #중복체크 이후에 nextIndex 를 찾아야 하는 이유가 있음
                #nextIndex 는 isduplication ==False 인 노드
                nextIndex = self._nextIndex (index , presult , maxindex)


                #중복 isduplication ==True 인경우에는 

                #처음 시작
                if cursor ==0  and value['context_words'] == False and value['isduplication'] == False :
                

                    value['pre-match'] = self.vstring [0 : value['span'][0]]

                    value ['context'] = context 

                    nextX = presult[nextIndex]['span'][0]

                    value ['next-match'] = self.vstring [ value['span'][1] : nextX ]

                    #키-값 추출
                    #키-추출
                    if value['key_values'] is None or len ( str(value['key_values']) ) < 1 :
                        value['extract-key'] = value ['match']
                    else:
                        value['extract-key'] = value ['key_values']

                    #값-추출
                    if value['pattern_structured_values'] is None or len ( str(value['pattern_structured_values']) ) < 1 :
                        
                        value['extract-value'] = value ['next-match']

                    else:
                        
                        value['extract-value'] = self._getRegexFirstWords(value['pattern_structured_values'] , value['match'] + value['next-match'] )
                        
                        #값을 추출했는데 일치하는 것이 없다면 영역을 따온다.
                        if value['extract-value'] is None or len ( str(value['extract-value']) ) < 1 :
                        
                            value['extract-value'] = value ['next-match']




                    cursor = value['span'][1]

                
                #다음 노드의 x 값과 현재노드의 y 값 사이의 값을 next-match 로 저장
                if cursor > 0 and index < maxindex and value['context_words'] == False and value['isduplication'] == False :
                    
                    
                    nextX = presult[nextIndex]['span'][0]

                    value ['next-match'] = self.vstring [ value['span'][1] : nextX ]

                    value ['context'] = context 


                  #키-값 추출-----------------------------------------------------------------------------------------------------
                    #키-추출
                    if value['key_values'] is None or len ( str(value['key_values']) ) < 1 :
                        value['extract-key'] = value ['match']
                    else:
                        value['extract-key'] = value ['key_values']

                    #값-추출
                    if value['pattern_structured_values'] is None or len ( str(value['pattern_structured_values']) ) < 1 :
                        
                        value['extract-value'] = value ['next-match']

                    else:
                        
                        value['extract-value'] = self._getRegexFirstWords(value['pattern_structured_values'] , value['match'] + value['next-match'] )
                        
                        #값을 추출했는데 일치하는 것이 없다면 영역을 따온다.
                        if value['extract-value'] is None or len ( str( value['extract-value'] ) ) < 1 :
                        
                            value['extract-value'] = value ['next-match']

                    #-----------------------------------------------------------------------------------------------------                            

                    cursor = value['span'][1]


                #마지막 노드인 경우            
                if cursor > 0 and index == maxindex and value['context_words'] == False :

                    nextX = len( self.vstring  )

                    value ['next-match'] = self.vstring[ value['span'][1] : nextX ]

                    value ['context'] = context 

                  #키-값 추출-----------------------------------------------------------------------------------------------------
                    #키-추출
                    if value['key_values'] is None or len ( str(value['key_values']) ) < 1 :
                        value['extract-key'] = value ['match']
                    else:
                        value['extract-key'] = value ['key_values']

                    #값-추출
                    if value['pattern_structured_values'] is None or len ( str(value['pattern_structured_values']) ) < 1 :
                        
                        value['extract-value'] = value ['next-match']

                    else:
                        
                        value['extract-value'] = self._getRegexFirstWords(value['pattern_structured_values'] , value['match'] + value['next-match'] )
                        
                        #값을 추출했는데 일치하는 것이 없다면 영역을 따온다.
                        if value['extract-value'] is None or len ( str( value['extract-value'] ) ) < 1 :
                        
                            value['extract-value'] = value ['next-match']

                    #-----------------------------------------------------------------------------------------------------                            



                    cursor = nextX


    def _getFilteringResult ( self ,presultList , pfilter):
        
        #관심있는 필드만 추출하여 [{}] 형태로 반환
        target_keys =pfilter
        result =[]

        for fordic in presultList:
            selected_values = {}
            for key in target_keys:
                if key in fordic:
                    selected_values[key] = fordic[key]

            result.append(selected_values)

        return result


    def run(self , ptarget_fields=['category_organs' , 'category_paths',  'pattern_keys'  ,'context' , 'pre-match' , 'match' , 'next-match' , 'extract-key' , 'extract-value']):

        result =None

        #패턴식들과 문장으로 정규식 실행
        result = self._regex_pattern_string ()

        #결과는 x좌표를 기준으로 오름차순 정렬
        result = sorted ( result , key =lambda p: p['span'][0])

        #좌표중복제거 등
        self._mergingResult ( result )

        #context 가 아니면서 중복이 아는 노드만 필터링
        result_temp = [x  for x in result if bool(x['context_words'])==False and x['isduplication']==False ] 

        #관심 키들만 필터링
        result = self._getFilteringResult(result_temp , ptarget_fields) 

        return result
    



# excel import , export ###############################################################
class clsRegexExcel:

    '''
    d = regexExcel.importExcel ('C:/Users/soshi/Desktop/20230810_regex_안치형/pattern_dict.xlsx' ) 
    regexExcel.exportExcel (d)
    '''

    def __init__ ( self ):
        pass

    @classmethod
    def importExcel (self ,pfilepath , psheetname=0) :
        
        data = pd.read_excel(pfilepath, sheet_name=psheetname)
        #data = np.where(np.isnan(data), None, data)
        data = data.where(pd.notna(data), '')
        
        return data.to_dict(orient='records')

    @classmethod
    def exportExcel (self , pdata, pfilepath =None  ) :

        df = pd.DataFrame(pdata)  # 데이터프레임 생성
        now = datetime.now()
        if pfilepath ==None :
            formatted_date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
            output_file =  formatted_date_time + '.xlsx' 
        else:
            output_file =  pfilepath

        df.to_excel(output_file, index=False)




def run(pExcelPath_patterns , pExcelPath_rowdata , pstringFieldname_rowdata , pExportRowCount=1000 ):


    #패턴식들 수집 ( import patterns )
    vpatterns = clsRegexExcel.importExcel (pExcelPath_patterns ) 


    #패턴 유효성 검사
    varr ='pk,category_organs,category_paths,context_words,pattern_headers,pattern_keys,key_values,key_heads,key_tails,pattern_structured_values,value_heads,value_tails,comment,comment2,comment3'
    varr = varr.split(',')

    for i in varr:
        if  i in vpatterns[0]:
            pass       
        else:
            print (i +  "유효하지 않음")
            exit()




    #문장수집 ( import rowdata )

        vstrings = clsRegexExcel.importExcel (pExcelPath_rowdata ) 


    #문장필드(키명칭)

        vfieldname_strings =pstringFieldname_rowdata


    #기타 전달필드들


    
        
    
    now = datetime.now()
    exportfilename = now.strftime("%Y_%m_%d_%H_%M_%S")

    vresult = []
    vctn =1
    for forstring in vstrings:
        
        
        exportfilename =  now.strftime("%Y_%m_%d_%H_%M_%S") + '__' + str(vctn) + '.xlsx' 

        obj = clsRegex( vpatterns , forstring[vfieldname_strings] )
        vresult = vresult + obj.run()

        if len( vresult ) >= pExportRowCount :

            clsRegexExcel.exportExcel (vresult , exportfilename )
            vresult=[]
            vctn = vctn + 1


        
        
    clsRegexExcel.exportExcel (vresult , exportfilename  )

    





