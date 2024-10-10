from langworld_db_data.removers.remover import Remover, RemoverError


class ListedValueRemoverError(RemoverError):
    pass


class ListedValueRemover(Remover):
    def remove_listed_value(
            self,
            id_of_value_to_remove: str,
    ) -> str:
        removed_value_information = ""
        self._remove_from_inventory_of_listed_values()
        self._remove_from_feature_profiles()

        if not removed_value_information:
            raise ListedValueRemoverError("Value not found. Perhaps it does not exist")
        else:
            return removed_value_information

    def _remove_from_inventory_of_listed_values(self):
        self._update_value_ids_in_inventory()

    def _remove_from_feature_profiles(self):
        pass

    def _update_value_ids_in_inventory(self):
        self._update_value_ids_in_feature_profiles()

    def _update_value_ids_in_feature_profiles(self):
        pass
