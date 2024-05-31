from .crud_view import CRUDView

class RacesView(CRUDView):
    collection_name = 'Races'
    
    def get(self, object_id=None):
        return super().get(object_id)

    def post(self):
        return super().post()

    def put(self, object_id):
        return super().put(object_id)

    def patch(self, object_id):
        return super().patch(object_id)

    def delete(self, object_id):
        return super().delete(object_id)
    
view_class = RacesView