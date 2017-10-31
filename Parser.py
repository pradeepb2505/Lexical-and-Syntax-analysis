from collections import deque
from TokGe import *
import re

def rule(rstring,tname,tprocess, antilookahead=[]):
    rule = []
   
    rstring = rstring.split()
    rule.append(rstring.pop(0))
    rule.append(rstring)
   
    rule.append([tname])
    rule.append(tprocess)
    rule.append(antilookahead)
    return rule

def parse(grammar,chart,tokens,startrule):

   
    def make_tree(tree, process):

        return process(tree)

    def addto(curpos, val):
        ref = val[:4]
        if ref not in reference[curpos]:
            chart[curpos].append(val)
            reference[curpos].append(ref)
            

    def closure(grammar,chart,token,curpos):
        for rule in grammar[token]:

            state = [rule[0],deque([]),deque(rule[1]),curpos,list(rule[2]),rule[3],rule[4]]
            addto(curpos,state)
    def nextstate(state,element):

        nextstate = [state[0],deque(state[1]),deque(state[2]),state[3],list(state[4]),state[5], state[6]]
        shifted = nextstate[2].popleft()
        nextstate[1].append(shifted)

        nextstate[4].append(element)
        
        return nextstate
        

    def shift(tokens,chart,state,curpos):

        
        if tokens[curpos] == state[2][0]:
            
            addto(curpos+1,nextstate(state,tokens[curpos].value))

    
    def reduction(origin,chart,equal,curpos,tree):
        
        for state in chart[origin]:
            
            if state[2] and state[2][0] == equal:
                
                addto(curpos,nextstate(state,tree))
        print chart
                
    
    reference = {}
    
    endline, endpos = tokens[-1].line, tokens[-1].col
    tokens.append(Token("endmarker",'eof',-1,-1,endline,endpos))
    
    for n in xrange(len(tokens)+1):
        chart[n] = []
        reference[n] = []
    chart[0].append([startrule[0],[],deque(startrule[1]),0,startrule[2],startrule[3],startrule[4]])

    for curpos in xrange(len(tokens)+1):
        
        if chart[curpos] == []:
            curtoken = tokens[curpos-1]
            raise Exception('Unexpected '+str(curtoken.value)+' at line '+str(curtoken.line)+' position '+str(curtoken.col)+'.')

        
        for state in chart[curpos]:
            
            equal = state[0]
            seen = state[1]
            unseen = state[2]
            origin = state[3]
            tree = state[4]
            process = state[5]
            antilookahead = state[6]

            if curpos == len(tokens)-1 and equal == startrule[0] and unseen == deque([]) and origin == 0:
                
                return make_tree(tree,process)
            if not unseen:
                if tokens[curpos] not in antilookahead:
                    tree = make_tree(tree,process)
                    reduction(origin,chart,equal,curpos,tree)
                else:
                    continue
            elif unseen[0][0] >= 'A' and unseen[0][0] <= 'Z':
                closure(grammar,chart,unseen[0],curpos)                
            else:
                shift(tokens,chart,state,curpos)


grammar=  {'S':[rule('S B','S->B',lambda p: (p[0],p[1]))],
           'B':[rule('B int mn pl pr be STM en','B->int main() begin STM end',lambda p: (p[0],p[6]))],
            'STM':[rule('STM STM STM','STM -> STM STM',lambda p:(p[0],p[1],p[2])),
                   rule('STM I','STM -> I',lambda p:(p[0],p[1])),
                   rule('STM IF','STM -> IF',lambda p: (p[0],p[1])),
                   rule('STM pr pl id pr scolon','STM->printf(id);',lambda p:(p[0]))],
           'IF':[rule('IF if pl EXPR pr be STM en','IF -> if(EXPR) begin STM end',lambda p:(p[0],p[3],p[6]))],
           'EXPR':[rule('EXPR EXPR re ex','EXPR->EXPR relop expr',lambda p:(p[0],p[1])),
                    rule('EXPR ex','EXPR->expr',lambda p:(p[0]))],
           'I':[rule('I int L scolon',"I->int L;",lambda p: (p[0],p[2]))],
          'L':[rule('L L comma id',"L->L,id",lambda p: (p[0],p[1])),rule('L id',"L->id",lambda p: (p[0]))]}
chart = {}       
lexer = [
         temp('int','int'),
         temp('mn','main'),
         temp('be','begin'),
         temp('en','end'),
         temp('if','if'),
         temp('ex','expr'),
         temp('re','relop'),
         temp('pr','printf'),
         temp('id','[A-Za-z]+[0-9]*'),
         temp('pl','\('),
         temp('pr','\)'),
         temp('int','[1-9][0-9]*',lambda a: int(a)),
         temp('comma','\,'),
         temp('space',' +',lambda a: None),
         temp('newline','\n',lambda a: None),
         temp('scolon',';'),
]

string = '''int main()
begin
int n1, n2, n3;
if( expr relop expr )
begin
printf( n1);
end
if ( expr relop expr relop expr )
begin
printf( n2);
end
if (expr relop expr )
begin
printf( n3);
end
end'''
try:
    a= parse(grammar, {}, lex(string, lexer), grammar['S'][0])
    print("\n\nProductions: \n\n")
    print a[0]
    b=str(a[1])
    c= re.split("\'*\'",b)
    for i in c:
        if i[0].isalpha():
            print (i)
except Exception,e:
    print "Syntax error: ",e.message

