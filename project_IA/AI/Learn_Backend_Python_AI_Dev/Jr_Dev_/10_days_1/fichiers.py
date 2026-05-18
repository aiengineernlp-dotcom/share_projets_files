####OPEN
# try:
#     fhand = open('mbox.txt')
#     print(fhand)
# except Exception as e:
#     print('the file does not existL:',e)

####READ FILES

# fname = input('Enter the file name: ')
# fhand = open(fname)
# count = 0
# for line in fhand:
#     count = count +1
# print('Line count:', count)
# ==========================================================================================================
# inp = fhand.read()
# print(len(inp))
# print(inp[:20])
# ==========================================================================================================

# for line in fhand:
#     #line = line.rstrip()
#     if line.startswith('From:'):
#         print(line)
# ==========================================================================================================
# try:
#     fname  =  input('Enter file name: ')
#     fhandle = open(fname)
#     count = 0
#     for line in fhandle:
#         if line.startswith('Subject: '):
#             print(line)
#             count = count +1
#     print(count,fname)
# except Exception as e:
#     print('this is the error', e)

s = 'spam - spam - spam'
delimeter = ''
print(s.split())
