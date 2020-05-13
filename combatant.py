from random import uniform

CLASS_STATS = {
    'TANK': {
        'strength': 10,
        'defense': 10,
        'agility': 1,
        'stamina': 3,
        'wisdom': 2
    }, 
    'MARTIAL ARTIST': {
        'strength': 7,
        'defense': 4,
        'agility': 8,
        'stamina': 9,
        'wisdom': 6
    }, 
    'TACTICIAN': {
        'strength': 2,
        'defense': 2,
        'agility': 5,
        'stamina': 8,
        'wisdom': 10
    }, 
    'BERSERKER': {
        'strength': 10,
        'defense': 4,
        'agility': 7,
        'stamina': 6,
        'wisdom': 1
    },
    'HEART': {
       'strength': 4,
        'defense': 8,
        'agility': 5,
        'stamina': 10,
        'wisdom': 4 
    }
}

CLASS_LIST = ['TANK', 'MARTIAL ARTIST', 'TACTICIAN', 'BERSERKER', 'HEART']

FIRST_NAMES = ['Xiao', 'Davey', 'Ken', 'Ryu', 'Bobobo', 'The', 'Henry', 'Xavier', 'Jason']
LAST_NAMES = ['Jenkins', 'Chen', 'Lee', 'Hisaishi', 'Johnson', 'Bobobobo', 'Chosen One', 'Moon', 'Sun', 'Balrog']

class Combatant:

    def __init__(self):
        self.combat_class = None
        self.strength = None
        self.defense = None
        self.agility = None
        self.stamina = None
        self.wisdom = None
        self.health = None
        self.rank = 'WARRIOR'
        self.name = None

        self.set_class()
        self.set_name()

    def set_name(self):
        fname_len = len(FIRST_NAMES)
        lname_len = len(LAST_NAMES)
        fname = FIRST_NAMES[round(uniform(0,fname_len-1))]
        lname = LAST_NAMES[round(uniform(0,lname_len-1))]
        self.name = "{0} {1}".format(fname, lname)

    def set_class(self):
        selector = round(uniform(0,4))
        self.combat_class = CLASS_LIST[selector]
        stats_dict = CLASS_STATS[self.combat_class]

        self.strength = stats_dict['strength']
        self.defense = stats_dict['defense']
        self.agility = stats_dict['agility']
        self.stamina = stats_dict['stamina']
        self.wisdom = stats_dict['wisdom']
        self.health = stats_dict['stamina'] * 4 + stats_dict['defense'] * 6

        # Assess Rank
        rank_dice_roll = uniform(0,1)
        bonus_count = 0

        if rank_dice_roll > 0.75:
            self.rank = 'ELITE'
            bonus_count = 1

        if rank_dice_roll > 0.90:
            self.rank = 'MASTER'
            bonus_count = 2

        if rank_dice_roll > 0.99:
            self.rank = 'LEGENDARY'
            bonus_count = 4

        stat_boost_hist = []
        while bonus_count > 0:
            bonus_count = bonus_count - 1

            stat_dice_roll = round(uniform(1,6))
            
            while stat_dice_roll in stat_boost_hist:
                stat_dice_roll = round(uniform(1,6))

            stat_boost_hist.append(stat_dice_roll)

            if stat_dice_roll == 1:
                self.strength = self.strength + 5
            elif stat_dice_roll == 2 :
                self.defense = self.defense + 5
            elif stat_dice_roll == 3:
                self.agility = self.agility + 5
            elif stat_dice_roll == 4:
                self.stamina = self.stamina + 5
            elif stat_dice_roll == 5:
                self.wisdom = self.wisdom + 5
            elif stat_dice_roll == 6:
                self.health = self.health * 1.5


    def print_stats(self):
        print("Combatant Name: {}".format(self.name))
        print("Combat Class: {}".format(self.combat_class))
        print("Combat Rank: {}".format(self.rank))
        print("Strength: {}".format(self.strength))
        print("Defense: {}".format(self.defense))
        print("Agility: {}".format(self.agility))
        print("Stamina: {}".format(self.stamina))
        print("Wisdom: {}".format(self.wisdom))
        print("Health: {}".format(self.health))

    def print_health(self):
        print("{0} has {1} health remaining...".format(self.name, self.health))


