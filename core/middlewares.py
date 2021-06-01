class CheckReservationsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # on each call, check current status of all reservations
        # it's a hack and it's a low effort one
        from bikes.models import Bike, BikeStatus

        for bike in Bike.objects.filter(status=BikeStatus.reserved):
            bike.check_reservation()

        response = self.get_response(request)

        return response
