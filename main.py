# This is a sample Python script.
import uefa_euro_2028
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from model.betty import Betty, Tournament, Team, Bet, Bettable, Bettor
import uefa_wc_2026
from datetime import datetime, timedelta
#from dotenv import load_dotenv

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #load_dotenv()
    betty = Betty()
    betty.drop_db()
    betty.setup_db()

#    print(betty.class_entity(Tournament))

#    t1 = Tournament(betty, "T1")
#    t2 = Tournament(betty, "T2", datetime.now())
#    t3 = Tournament(betty, "FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21),
#                    datetime(day=19, month=7, year=2026, hour=21))
#    print(f'{t1.name} / {t2.name} / {t3.name}')
#    betty.save(t3)

    uefa_wc_2026.setup(betty)
    uefa_euro_2028.setup(betty)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
