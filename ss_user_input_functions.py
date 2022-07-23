def ask_if_custom_setup(first_time: bool = True) -> bool:
    """Asks user if they want to customize the setup."""
    
    thing = 'your setup'
    adjective = 'the default'
    verb = 'Stick'
    if not first_time:
        thing = 'something else'
        adjective = 'your custom'
        verb = 'Go'

    while True:
        wants_to_customize = input(f'Do you want to customize {thing}? (yes / no)\n> ').lower()
        if wants_to_customize == 'yes':
            wants_to_customize = True
            break
        if wants_to_customize == 'no':
            wants_to_customize = False
            print(f'Ok. {verb}ing with {adjective} settings.\n')
            break
        print("I'm sorry, I don't understand. Let's try again:")

    return wants_to_customize


def choose_custom_setup() -> str:
    while True:
        user_choice = input('Please choose: canvas [1]\tmargin\t[2]\tgrid [3]\n> ').lower()
        if user_choice in ['canvas', '1', 'canvas [1]']:
            user_choice = 'canvas'
            break
        if user_choice in ['margin', '2', 'margin [2]']:
            user_choice = 'margin'
            break
        if user_choice in ['grid', '3', 'grid [3]']:
            user_choice = 'grid'
            break
        print("I'm not sure I understand. Let's try again:")
    return user_choice


def customize_canvas():
    pass

def customize_margin():
    pass

def customize_grid():
    pass