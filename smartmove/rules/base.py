class CityRules:
    def on_unlock(self, vehicle, user):
        raise NotImplementedError("on_unlock must be implemented by city rule classes")

    def on_end_rental(self, rental):
        raise NotImplementedError("on_end_rental must be implemented by city rule classes")

    def validate_movement(self, vehicle):
        return True
