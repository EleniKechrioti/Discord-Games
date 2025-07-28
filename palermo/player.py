class Player:
    def __init__(self, display_name, user_id,role=None):
        self.display_name = display_name
        self.user_id = user_id
        self.role = role
        self.alive = True
        self.votes = 0

    def set_role(self, role):
        self.role = role

    def get_role(self):
        return self.role

    def is_alive(self):
        return self.alive
    
    def die(self):
        print("psofa gamo.")
        self.alive = False

    def add_vote(self):
        self.votes += 1

    def reset_votes(self):
        self.votes = 0    

    def getUserId(self):
        return self.user_id




