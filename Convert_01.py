import codecs
from datetime import date, timedelta

assignments = []
total_assignments = 0
solved_assignments = 0
comments = []

def write_assignments(newfilename, assignments, total_assignments, comments):
    today = date.today()
    today_str = today.strftime("%d.%m.%Y")

    ff = codecs.open(newfilename, "w", encoding = 'utf-8-sig')
    for item in assignments:
        ff.write('$\n')
        ff.write(item[0] + '\n')
        ff.write('%\n')
        ff.write(item[1] + '\n')
        ff.write('@\n')
        ff.write('0 ' + today_str + '\n')
    for c in comments:
        ff.write('& ' + c  + '\n')
    ff.close()

now = date.today()
oldfilename = input("Old Filename: ")
f = codecs.open(oldfilename, 'r', encoding = 'utf-8-sig')
line = f.readline().strip()

while True:
    try:
        if (len(line) == 0):
            line = f.readline().strip()
            continue
        ch = line[0]
        if (ch == '&'):
            break
        if (ch == '$'):
        # читаем следующие две единицы информации и добавляем юнит в список assignment
            new_item = []
            next_string = ''
            line = f.readline().strip()
            while line[0] != '%':
                next_string += line
                line = f.readline().strip()
                if line[0] != '%':
                    next_string += '\n'
            new_item.append(next_string)
            next_string = ''
            line = f.readline().strip()
            while line[0] != '$' and line[0] != '&':
                next_string += line
                line = f.readline().strip()
                if line[0] != '$' and line[0] != '&':
                    next_string += '\n'
            new_item.append(next_string)
            new_item += [0, 0, 0]
            assignments.append(new_item)
            total_assignments += 1
            continue
        line = f.readline().strip()
    except EOFError:
        break

while line:
    comments.append(line[1:].strip())
    line = f.readline().strip()

f.close()

newfilename = input("New Filename: ")

write_assignments(newfilename, assignments, total_assignments, comments)

print("All done!")

