from langworld_db_data.removers.remover import Remover, RemoverError

class ListedValueRemoverError(RemoverError):
    pass


class ListedValueRemover(Remover):
    def remove_listed_value(self):
        self._remove_from_inventory_of_listed_values()

    def _remove_from_inventory_of_listed_values(self):
        pass

    def _remove_from_feature_profiles(self):
        pass
