level = open('intro.txt', 'w')
level.write('/' * 20 + '\n')
for i in range(18):
    level.write('/' + ' ' * 18 + '/' + '\n')
level.write('/' * 20 + '\n')

level.close()
