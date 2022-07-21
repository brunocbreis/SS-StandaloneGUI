class GlobalWealth(object):
    def __init__(self):
        self._global_wealth = 10.0
        self._observers = [] 

    @property
    def global_wealth(self):
        return self._global_wealth

    @global_wealth.setter
    def global_wealth(self, value):
        self._global_wealth = value # 4. every time i set the value...
        for callback in self._observers: # 5. for every item in the list of observers...
            print('announcing change')
            callback(self._global_wealth) # 6. i run the function with this parameter as an argument

    def bind_to(self, callback):
        print('bound')
        self._observers.append(callback) # 3. appends p.update_how_happy to the list of observers


class Person(object):
    def __init__(self, data):
        self.wealth = 1.0
        self.data: GlobalWealth = data # 1. now the person is connected to the global wealth object
        self.data.bind_to(self.update_how_happy) # 2. calls the function that binds the person to the globalwealth
        self.happiness = self.wealth / self.data.global_wealth

    def update_how_happy(self, global_wealth):
        self.happiness = self.wealth / global_wealth


if __name__ == '__main__':
    data = GlobalWealth()
    p = Person(data)
    print(p.happiness)
    data.global_wealth = 1.0
    print(p.happiness)