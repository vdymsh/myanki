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

class Deck:
    def __init__(self, items = [], count = 0, comments = []):
        self.items = items
        self.count = count
        self.comments = comments

    def write_items(self, filename):
        ff = codecs.open(filename, "w", encoding = 'utf-8-sig')
        for item in self.items:
            ff.write('$\n')
            ff.write(item.question + '\n')
            ff.write('%\n')
            ff.write(item.answer + '\n')
            ff.write('@\n')
            ff.write(str(item.right_count) + ' '
                     + str(item.right_answer_day) + '.'
                     + str(item.right_answer_month) + '.'
                     + str(item.right_answer_year) + '\n')
        for c in self.comments:
            ff.write('& ' + c  + '\n')
        ff.close()

class Assignments:
    def __init__(self, items = [], count = 0,
                 indexes = [],     # index list of items for this session's active assignments
                 solved = 0):  # count of solved assignments during the session
        self.items = items
        self.count = count
        self.indexes = indexes
        self.solved = solved

deck = Deck()          # list of question - answer item read from file
assignments = Assignments() # list of question - answer item included in assigned items

data_file = ""          # filename for questions - answers collection
chunk_count = 30        # max count of assignments for the session
right_answers = 1
right_after_wrong_answers = 2
pauses = (0, 1, 2, 4, 8, 16, 32, 64,)

today = date.today()
today_str = today.strftime("%d.%m.%Y")

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

            # add item to the deck
            deck.items.append(new_item)
            deck.count += 1

            # включаем ли new_item в assignments?
            if assignments.count < chunk_count:
                last_date = date(new_item.right_answer_year,
                                 new_item.right_answer_month,
                                 new_item.right_answer_day)
                if last_date + timedelta(pauses[new_item.right_count]) <= today:
                    assignments.items.append(new_item)
                    assignments.count += 1
                    assignments.indexes.append([item_ndx, 1, 0, 0])
                    item_ndx += 1

            line = f.readline().strip()
            continue

        line = f.readline().strip()
    except EOFError:
        break

while line:
    deck.comments.append(line[1:].strip())
    line = f.readline().strip()

f.close()

while assignments.solved < assignments.count:
    today_str = today.strftime("%d.%m.%Y")
    for aitems in assignments.indexes:
        if aitems[1] == 0:
            continue
        item = assignments.items[aitems[0]]
#        item[2] += 1
        print(item.question)
        ans = input("Answer: ")
        print(item.answer)
        while True:
            res = int(input("Yes(1) / No(0) / Break(9): "))
            if (res == 9):
                assignments.solved = assignments.count
                break
            elif (res == 0):
                aitems[2] += 1
                aitems[3] = 0
                assignments.items[aitems[0]].right_count = 0
                break
            elif (res == 1):
                aitems[2] += 1
                aitems[3] += 1

                if aitems[2] == aitems[3] and aitems[3] >= right_answers:
                    aitems[1] = 0
                    assignments.solved += 1
                    assignments.items[aitems[0]].right_answer_day = today.day
                    assignments.items[aitems[0]].right_answer_month  = today.month
                    assignments.items[aitems[0]].right_answer_year  = today.year
                    assignments.items[aitems[0]].right_count += 1
                elif aitems[3] >= right_after_wrong_answers:
                    aitems[1] = 0
                    assignments.solved += 1
                    assignments.items[aitems[0]].right_answer_day = today.day
                    assignments.items[aitems[0]].right_answer_month = today.month
                    assignments.items[aitems[0]].right_answer_year = today.year
                break
            else:
                continue
        if (assignments.solved == assignments.count):
            break

res = int(input("Save(1) / Save As...(2) / Don't Save(0): "))
if res == 2:
    data_file = input("Filename: ")

if res == 1 or res == 2:
    deck.write_items(data_file)

print("All done!")
