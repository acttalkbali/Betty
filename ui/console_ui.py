#================== Basic UI console functions

def int_or_none(s:str)->int|None:
    """
    converts and returns the supplied string to an int if it represents a valid number, or else return None
    :param s:
    :return:
    """
    try:
        n = int(s)
    except:
        n = None
    return n

def input_int(prompt:str, n_min:int, n_max:int)->int:
    """
    Request an int in the range [n_min .. n_max]
    :param prompt: The prompt to display
    :param n_min:
    :param n_max:
    :return:
    """
    n = None
    while n is None or n < n_min or n > n_max:
        n = int_or_none(input(f"{prompt} [{n_min}-{n_max}] : "))
    return n

def input_selection(options:list, fn: callable|None=None, exit_option=0)->int:
    """
    :param options:
    :param fn: a 'key' function for the option, used for display
    :return: -1 if exit menu selected else the index of the chosen selection
    """
    if exit_option == 0:
        print("0: exit menu")

    for i, option in enumerate(options):
        print(f"{i+1}: {fn(option) if fn else option}")
    return input_int("Your selection", 0 if exit_option==0 else 1, len(options)) - 1 # -1 so it can be used as an index

def error_msg(msg:str)->None:
    """
    Displays an error message
    :param msg:
    :return:
    """
    print(f"*** {msg} ***")

def yes_no(question:str) -> bool:
    """
    Input a yes / no choice
    :param question: the question for which the response is due
    :return: True if answer is yes, False if the answer is no
    """
    answer = ''
    while answer not in ['y', 'n']:
        answer = input(f"{question} [y/n] : ").lower()
    return answer == 'y'

def info(msg:str)->None:
    """
    displays an informational message
    :param msg:
    :return:
    """
    print(msg)
