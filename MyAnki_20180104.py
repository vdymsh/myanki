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

# Full deck of questions - answers in the input file
class Deck:
    def __init__(self, items = [], count = 0, solved_count = 0, comments = []):
        self.items = items
        self.count = count
        self.solved_count = solved_count
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

class NdxUnit:
    def __init__(self, ndx, active = True, answers = 0, continuous_answers = 0):
        self.ndx = ndx
        self.active = active
        self.answers = answers
        self.continuous_answers = continuous_answers

class Assignment:
    def __init__(self, items = [], count = 0,
                 indexes = [],     # index list of items for this session's active assignment
                 solved = 0):  # count of solved assignment during the session
        self.items = items
        self.count = count
        self.indexes = indexes
        self.solved = solved


# configuration defaults
data_file = "MyAnkiData.txt"
chunk_count = 30
right_answers = 1
right_after_wrong_answers = 2
pauses = (0, 1, 2, 4, 8, 16, 32, 64,)

deck = Deck()          # list of question - answer item read from file
assignment = Assignment() # list of question - answer item included in assigned items

today = date.today()
# today_str = to0day.strftime("%d.%m.%Y")

# Reading .cfg file
try:
    with open("MyAnki_20180104.cfg", "r") as ff:
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
        # читаем следующие две единицы информации и добавляем item в список assignment
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
            last_date = date(new_item.right_answer_year,
                             new_item.right_answer_month,
                             new_item.right_answer_day)
            if last_date + timedelta(pauses[new_item.right_count]) > today:
                deck.solved_count += 1

            # включаем ли new_item в assignment?
            if assignment.count < chunk_count:
                if last_date + timedelta(pauses[new_item.right_count]) <= today:
                    assignment.items.append(new_item)
                    assignment.count += 1
                    assignment.indexes.append(NdxUnit(item_ndx))
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

print(" Total questions in the file :", deck.count)
print("Solved questions in the file :", deck.solved_count)
print("Num of questions in the chunk:", assignment.count)

while assignment.solved < assignment.count:
    for aitems in assignment.indexes:
        if not aitems.active:
            continue
        item = assignment.items[aitems.ndx]
        print("Question N:", aitems.ndx + 1)
        print(item.question)
        ans = input("Answer: ")
        print(item.answer)
        while True:
            input_str = input("Yes(1) / No(0) / Break(9): ")
            if not input_str in ('0', '1', '9',):
                input_str = input("Yes(1) / No(0) / Break(9): ")
            if not input_str in ('0', '1', '9',):
                print("Wrong input. Default: '0'")
                input_str = '0';
            res = int(input_str)
            if (res == 9):
                assignment.solved = assignment.count
                break
            elif (res == 0):
                aitems.answers += 1
                aitems.continuous_answers = 0
                assignment.items[aitems.ndx].right_count = 0
                break
            elif (res == 1):
                aitems.answers += 1
                aitems.continuous_answers += 1

                if aitems.answers == aitems.continuous_answers and aitems.continuous_answers >= right_answers:
                    aitems.active = False
                    assignment.solved += 1
                    assignment.items[aitems.ndx].right_answer_day = today.day
                    assignment.items[aitems.ndx].right_answer_month  = today.month
                    assignment.items[aitems.ndx].right_answer_year  = today.year
                    assignment.items[aitems.ndx].right_count += 1
                elif aitems.continuous_answers >= right_after_wrong_answers:
                    aitems.active = False
                    assignment.solved += 1
                    assignment.items[aitems.ndx].right_answer_day = today.day
                    assignment.items[aitems.ndx].right_answer_month = today.month
                    assignment.items[aitems.ndx].right_answer_year = today.year
                break
            else:
                continue
        if (assignment.solved == assignment.count):
            break

input_str = input("Save(1) / Save As...(2) / Don't Save(0): ")
if not input_str in ('0', '1', '2',):
    input_str = input("Save(1) / Save As...(2) / Don't Save(0): ")
if not input_str in ('0', '1', '2',):
    print("Wrong input. Default: '0'")
    input_str = '0';
res = int(input_str)
if res == 2:
    data_file = input("Filename: ")

if res == 1 or res == 2:
    deck.write_items(data_file)

print("All done!")
