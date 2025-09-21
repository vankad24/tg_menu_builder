class Scope:
    def __init__(self, vars_dict, parent_scope=None, message=None, scopeRep=None):
        self.scopeRep = scopeRep
        self.parent_scope = parent_scope
        self.vars_dict = vars_dict
        self.message = message

    def __getitem__(self, key):
        if key in self.vars_dict:
            return self.vars_dict[key]
        if self.parent_scope is not None:
            return self.parent_scope[key]
        return self.scopeRep.get_reserved_var(self, key)


