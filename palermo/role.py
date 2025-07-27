class Role:
    def __init__(self, role_name, description, alignment="Neutral"):
        self.role_name = role_name
        self.description = description
        self.alignment = alignment

    def set_rolename(self, role):
        self.role_name = role

    def get_rolename(self):
        return self.role_name

    def set_description(self, description):
        self.description = description
    
    def get_description(self):
        return self.description
    
    def set_alignment(self, alignment):
        self.alignment = alignment
    
    def get_alignment(self):
        return self.alignment