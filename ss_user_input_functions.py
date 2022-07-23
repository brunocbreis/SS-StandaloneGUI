# Setup input functions
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
        if wants_to_customize in ['yes','y']:
            wants_to_customize = True
            break
        if wants_to_customize in ['no', 'n']:
            wants_to_customize = False
            print(f'Ok. {verb}ing with {adjective} settings.')
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

def customize_canvas() -> list[int]:
    attributes = ['Width','Height']
    custom_values = []
    for attribute in attributes:
        user_choice = input(f"{attribute}: ")
        while not user_choice.isnumeric():
            print('Please only type in numbers.')
            user_choice = input(f"{attribute}: ")
        custom_values.append(int(user_choice))
    return custom_values

def customize_margin() -> list[int]:
    attributes = ['Top', 'Left', 'Bottom', 'Right']
    custom_values = []
    for attribute in attributes:
        user_choice = input(f"{attribute}: ")
        while not user_choice.isnumeric():
            print('Please only type numbers.')
            user_choice = input(f"{attribute}: ")
        custom_values.append(int(user_choice))
    return custom_values

def customize_grid() -> list[int]:
    attributes = ['Cols', 'Rows', 'Gutter (px)']
    custom_values = []
    for attribute in attributes:
        user_choice = input(f"{attribute}: ")
        while not user_choice.isnumeric():
            print('Please only type numbers.')
            user_choice = input(f"{attribute}: ")
        custom_values.append(int(user_choice))
    return custom_values


# Screen input functions
def ask_if_more_screens() -> bool:
    while True:
        wants_more_screens = input('Do you want to create another Screen? (yes / no)\n> ').lower()
        if wants_more_screens in ['yes', 'y']:
            wants_more_screens = True
            break
        if wants_more_screens in ['no', 'n']:
            wants_more_screens = False
            break
        print("Come on. It's a yes or no question.")

    return wants_more_screens

def screen_config() -> list[int]:
    attributes = [
        'Width (cols)',
        'Height (rows)',
        'X Position (leftmost col #)',
        'Y Position (top row #)'
        ]
    custom_values = []
    for attribute in attributes:
        user_choice = input(f"{attribute}: ")
        while not user_choice.isnumeric():
            print('Numbers only please.')
            user_choice = input(f"{attribute}: ")
        custom_values.append(int(user_choice))
    return custom_values

def screen_config_coords() -> list[int]:
    pass

