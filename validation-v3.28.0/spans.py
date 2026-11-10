import re
# Skip complete strings and nested template expressions while locating function bodies.
def string_end(code,i):
 quote=code[i];i+=1
 while i<len(code):
  if code[i]=='\\':i+=2;continue
  if code[i]==quote:return i+1
  if quote=='`'and code.startswith('${',i):i=balanced_end(code,i+1,'{','}');continue
  i+=1
 raise ValueError('Unterminated string')
def balanced_end(code,i,left='{',right='}'):
 depth=0
 while i<len(code):
  c=code[i]
  if c in "'\"`":i=string_end(code,i);continue
  if code.startswith('//',i):
   j=code.find('\n',i);i=len(code)if j<0 else j+1;continue
  if code.startswith('/*',i):i=code.index('*/',i+2)+2;continue
  if c==left:depth+=1
  if c==right:
   depth-=1
   if depth==0:return i+1
  i+=1
 raise ValueError('Unterminated block')
def span(code,name):
 m=re.search(r'^function '+re.escape(name)+r'\(',code,re.M)
 if not m:raise ValueError('Missing function '+name)
 start=m.start();i=balanced_end(code,m.end()-1,'(',')')
 while code[i].isspace():i+=1
 assert code[i]=='{',(name,code[i:i+30])
 return start,balanced_end(code,i)
