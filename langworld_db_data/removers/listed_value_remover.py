from langworld_db_data.removers.remover import Remover, RemoverError


class ListedValueRemoverError(RemoverError):
    pass


class ListedValueRemover(Remover):
    def remove_listed_value(self):
        self._remove_from_inventory_of_listed_values()
        self._remove_from_feature_profiles()

    def _remove_from_inventory_of_listed_values(self):
        self._update_value_ids_in_inventory()

    def _remove_from_feature_profiles(self):
        pass

    def _update_value_ids_in_inventory(self):
        self._update_value_ids_in_feature_profiles()

    def _update_value_ids_in_feature_profiles(self):
        pass
