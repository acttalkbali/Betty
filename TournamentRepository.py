from abc import ABC

class TournamentRepository(ABC):
    def __init__(self, tournament_name):
        super().__init__()
        self._tournament_name = tournament_name

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def load_user_view(self):
        '''
        Loads user-related data for this tournament
        :param tournament_name:
        :return:
        '''
        raise NotImplementedError

    def load_admin_view(self):
        '''
        loads admin-related data for this tournament
        :param tournament_name:
        :return:
        '''
        raise NotImplementedError

class TournamentRepositoryFactory():
    def __init__(self, cls: TournamentRepository, *agrs, **kwargs):
        cls.__init__(*args, **kwargs)

