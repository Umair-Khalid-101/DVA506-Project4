from rules.base import CityRules

class MilanRules(CityRules):
    def on_unlock(self, vehicle, user):
        if not vehicle.helmet_present:
            raise Exception("Helmet not detected")
