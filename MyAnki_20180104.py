import codecs
from datetime import date, timedelta

class Item:
    def __init__(self, question = '', answer = '', right_count = 0,
                 right_answer_year = 1970, right_answer_month = 1,
                 right_answer_day = 1):
        self.question = question
        self.answer = answer
        self.right_count = right_count
        self.right_answer_year = right_answer_year
        self.right_answer_month = right_answer_month
        self.right_answer_day = right_answer_day

items = []              # list of question - answer item read from file
assignments = []        # list of question - answer item included in assigned items
assigned_items = []     # index list of items for this session's active assignments
total_items = 0         # total count of items in data file
total_assignments = 0   # total count of assignments for the session
solved_assignments = 0  # count of solved assignments during the session
comments = []

data_file = ""          # filename for questions - answers collection
chunk_count = 30        # max count of assignments for the session
right_answers = 1
right_after_wrong_answers = 2
pauses = (0, 1, 2, 4, 8, 16, 32, 64,)

today = date.today()
today_str = today.strftime("%d.%m.%Y")

def write_items(filename, items, total_items, comments):
    ff = codecs.open(filename, "w", encoding = 'utf-8-sig')
    for item in items:
        ff.write('$\n')
        ff.write(item.question + '\n')
        ff.write('%\n')
        ff.write(item.answer + '\n')
        ff.write('@\n')
        ff.write(str(item.right_count) + ' '
                 + str(item.right_answer_day) + '.'
                 + str(item.right_answer_month) + '.'
                 + str(item.right_answer_year) + '\n')
    for c in comments:
        ff.write('& ' + c  + '\n')
    ff.close()

# Reading .cfg file
try:
    with open("MyAnki_20171227.cfg", "r") as ff:
        data_file = ff.readline().strip()
        chunk_count = int(ff.readline().strip())
        right_answers = int(ff.readline().strip())
        right_after_wrong_answers = int(ff.readline().strip())
        pauses = eval(ff.readline().strip())
except:
    print("Error with reading cfg file - using defaults")

'''
print(data_file)
print(chunk_count)
print(right_answers)
print(right_after_wrong_answers)
print(pauses)
'''

# new_filename = input("Filename: ")

f = codecs.open(data_file, 'r', encoding = 'utf-8-sig')
line = f.readline().strip()
item_ndx = 0

while line:
    try:
        if (len(line) == 0):
            line = f.readline().strip()
            continue
        ch = line[0]
        if (ch == '&'):
            break
        if (ch == '$'):
        # читаем следующие две единицы информации и добавляем item в список assignments
            new_item = Item()
            next_string = ''
            line = f.readline().strip()
            while line[0] != '%':
                next_string += line
                line = f.readline().strip()
                if line[0] != '%':
                    next_string += '\n'
            new_item.question = next_string    # question
            next_string = ''
            line = f.readline().strip()
            while line[0] != '@':
                next_string += line
                line = f.readline().strip()
                if line[0] != '@':
                    next_string += '\n'
            new_item.answer = next_string    # answer
            line = f.readline().strip()
            data = list(line.split())
            new_item.right_count = int(data[0])
            ds, ms, ys = data[1].split('.')
            new_item.right_answer_year = int(ys)
            new_item.right_answer_month = int(ms)
            new_item.right_answer_day = int(ds)
            items.append(new_item)
# включаем ли new_item в assignments?
            if total_assignments < chunk_count:
                last_date = date(new_item.right_answer_year,
                                 new_item.right_answer_month,
                                 new_item.right_answer_day)
                if last_date + timedelta(pauses[new_item.right_count]) <= today:
                    assignments.append(new_item)
                    total_assignments += 1
                    assigned_items.append([item_ndx, 1, 0, 0])
                    item_ndx += 1
# --- включаем ли new_item в assignments?
            total_items += 1
            line = f.readline().strip()
            continue

        line = f.readline().strip()
    except EOFError:
        break

while line:
    comments.append(line[1:].strip())
    line = f.readline().strip()
f.close()

'''
for c in comments:
    print(c)
'''

'''
for item in items:
    print(item[0])
    print(item[1])
    print(item[2], item[3])
'''

while solved_assignments < total_assignments:
    today_str = today.strftime("%d.%m.%Y")
#    print(today_str)
    for aitems in assigned_items:
        if aitems[1] == 0:
            continue
        item = assignments[aitems[0]]
#        item[2] += 1
        print(item.question)
        ans = input("Answer: ")
        print(item.answer)
        while True:
            res = int(input("Yes(1) / No(0) / Break(9): "))
            if (res == 9):
                solved_assignments = total_assignments
                break
            elif (res == 0):
                aitems[2] += 1
                aitems[3] = 0
                assignments[aitems[0]].right_count = 0
                break
            elif (res == 1):
                aitems[2] += 1
                aitems[3] += 1

                if aitems[2] == aitems[3] and aitems[3] >= right_answers:
                    aitems[1] = 0
                    solved_assignments += 1
                    assignments[aitems[0]].right_answer_day = today.day
                    assignments[aitems[0]].right_answer_month  = today.month
                    assignments[aitems[0]].right_answer_year  = today.year
                    assignments[aitems[0]].right_count += 1
                elif aitems[3] >= right_after_wrong_answers:
                    aitems[1] = 0
                    solved_assignments += 1
                    assignments[aitems[0]].right_answer_day = today.day
                    assignments[aitems[0]].right_answer_month = today.month
                    assignments[aitems[0]].right_answer_year = today.year
                break
            else:
                continue
        if (solved_assignments == total_assignments):
            break

res = int(input("Save(1) / Save As...(2) / Don't Save(0): "))
if res == 2:
    data_file = input("Filename: ")

if res == 1 or res == 2:
    write_items(data_file, items, total_items, comments)

print("All done!")
