from src.menu_builder.repository.AccessRepository import AccessRepository
from src.menu_builder.repository.FunctionRepository import FunctionRepository
from src.menu_builder.repository.MenuRepository import MenuRepository
from src.menu_builder.repository.ScopeRepository import ScopeRepository
from src.menu_builder.repository.TranslationRepository import TranslationRepository


class RepositoryStorage:
    def __init__(self,
                 funRep: FunctionRepository,
                 transRep: TranslationRepository,
                 scopeRep: ScopeRepository,
                 accessRep: AccessRepository,
                 menuRep: MenuRepository):

        funRep_types = (FunctionRepository,)
        transRep_types = (TranslationRepository,)
        scopeRep_types = (ScopeRepository,)
        accessRep_types = (AccessRepository,)
        menuRep_types = (MenuRepository,)

        if not isinstance(funRep, funRep_types):
            raise TypeError(f"funRep должен быть экземпляром {funRep_types}")

        if not isinstance(transRep, transRep_types):
            raise TypeError(f"transRep должен быть экземпляром {transRep_types}")

        if not isinstance(scopeRep, scopeRep_types):
            raise TypeError(f"scopeRep должен быть экземпляром {scopeRep_types}")

        if not isinstance(accessRep, accessRep_types):
            raise TypeError(f"accessRep должен быть экземпляром {accessRep_types}")

        if not isinstance(menuRep, menuRep_types):
            raise TypeError(f"menuRep должен быть экземпляром {menuRep_types}")

        self.funRep: FunctionRepository = funRep
        self.transRep: TranslationRepository = transRep
        self.scopeRep: ScopeRepository = scopeRep
        self.accessRep: AccessRepository = accessRep
        self.menuRep: MenuRepository = menuRep
