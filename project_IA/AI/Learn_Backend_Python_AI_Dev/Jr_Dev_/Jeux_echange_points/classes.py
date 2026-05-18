class Player:
    def __init__(self, name, qty_life):
        self.name = name
        self.qty_life = qty_life
    def __str__(self):
        return f"Nom du joueur : {self.name}\nQuantite de vie: {self.qty_life}"

    def donner_points(self,other_player,amount):
        try:
            if self.qty_life >= amount:
                self.qty_life = self.qty_life - amount
                other_player.qty_life = other_player.qty_life + amount
                print(f'{self.name}: tu as donné {amount} points a {other_player.name} il te reste:{self.qty_life}')
                print(f'{other_player.name}: tu as recu {amount} points de {self.name} il te reste:{other_player.qty_life}')
        except Exception as e:
            print('This is the error:', e)
        else:
            print(f'{self.name} ne peut donner de points a {other_player.name}')

    def display_life(self):
        try:
            print(f'{self.name}:Il te reste: {self.qty_life} points')
        except Exception as e:
            print('This is the error: ', e)


