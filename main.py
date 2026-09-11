# This is a sample Python script.
import uefa_euro_2028
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from model.betty import Betty, Tournament, Team, Bet, Bettable, Bettor
import uefa_wc_2026
from datetime import datetime, timedelta

from model.storable import Storable

#from dotenv import load_dotenv

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #load_dotenv()
    #betty = Betty()
    print(Storable.create_schema())
    print(Storable.drop_schema())
    #betty.drop_db()
    #betty.setup_db()

    #uefa_wc_2026.setup(betty)
    #uefa_euro_2028.setup(betty)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
