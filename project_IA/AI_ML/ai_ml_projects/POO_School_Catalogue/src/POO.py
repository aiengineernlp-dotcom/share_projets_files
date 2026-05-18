class School:
    def __init__(self, name: str, level=None, numberOfStudents: int = 0):
        self.name = name
        self.level = level if level is not None else []
        self.numberOfStudents = numberOfStudents

    def __repr__(self):
        return f"Name: {self.name}\n" f"Levels: {self.level}\n" f"NumberOfStudents: {self.numberOfStudents}"

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        if isinstance(new_name, str):
            self.name = new_name
        else:
            raise TypeError("Name must be a string")

    def get_level(self):
        return self.level

    def set_level(self, new_level):
        if isinstance(new_level, str):
            self.level = new_level
        else:
            return TypeError("Level must be a string")

    def get_numberOfStudents(self):
        return self.numberOfStudents

    def set_numberOfStudents(self, new_numberOfStudents):
        if isinstance(new_numberOfStudents, int):
            self.numberOfStudents = new_numberOfStudents
        else:
            raise TypeError("NumberOfStudents must be an integer")


class Primary(School):
    def __init__(self, name: str, pickupPolicy: str, level=None, numberOfStudents: int = 0, ):
        super().__init__(name, level, numberOfStudents)
        self.pickupPolicy = pickupPolicy

    def get_pickupPolicy(self):
        return self.pickupPolicy

    def set_pickupPolicy(self, new_pickup_policy):
        if isinstance(new_pickup_policy, str):
            self.pickupPolicy = new_pickup_policy
        else:
            raise TypeError("pickupPolicy must be a string")

    def __repr__(self):
        base = super().__repr__()
        return base + f"\nPickupPolicy: {self.pickupPolicy}"


class Middle(School):
    pass


class HighSchool(School):
    def __init__(self, name: str, level=None, numberOfStudents: int = 0, sportsTeams=None):
        super().__init__(name, level, numberOfStudents)
        self.sportsTeams = sportsTeams if sportsTeams is not None else []

    def get_sportsTeams(self):
        return self.sportsTeams

    def set_sportsTeams(self, new_sportsTeams):
        if isinstance(new_sportsTeams, list):
            self.sportsTeams = new_sportsTeams
        else:
            raise TypeError("this must be a list")

    def __repr__(self):
        base = super().__repr__()
        return base + f"\nSportsTeams: {self.sportsTeams}"

sc = School("name_School_old", ['primary','high','middle'])
print(sc)
print("=============")
sc.get_name()
sc.set_name("name_School_new", )
print(sc)

print("\n================")
ps = Primary(pickupPolicy="name_School_new", name="name_School_new", level="primary")
print(ps)
ps.get_name()
print(ps)

print("\n================")
hs = School("hs_1", level="high")
print(hs)



