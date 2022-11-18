from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Attendee, ConferenceVO
from django.views.decorators.http import require_http_methods
from .models import AccountVO
import json


class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceVODetailEncoder(),
    }

    # def get_extra_data(self, o):
    #     return {"has_account": True if AccountVO.objects.filter(email=o.email).count() > 0 else False}        # else:
    def get_extra_data(self, o):
        count = AccountVO.objects.filter(email=o.email).count()
        if count > 0:
            return {
                "has_account": True,
            }
        else:
            return {
                "has_account": False,
            }

        # Get the count of AccountVO objects with email equal to o.email
        # Return a dictionary with "has_account": True if count > 0
        # Otherwise, return a dictionary with "has_account": False


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_vo_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            conference_href = f'/api/conferences/{conference_vo_id}/'
            conference = ConferenceVO.objects.get(import_href=conference_href)
            content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )
        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )

    # attendee = Attendee.objects.get(id=conference_id)
    # return JsonResponse(
    #     {
    #         "attendees": [
    #             {
    #                 "name": attendee.name,
    #                 "href": attendee.get_api_url(),
    #             },
    #         ],
    #     }
    # )
    """
    Lists the attendees names and the link to the attendee
    for the specified conference id.

    Returns a dictionary with a single key "attendees" which
    is a list of attendee names and URLS. Each entry in the list
    is a dictionary that contains the name of the attendee and
    the link to the attendee's information.

    {
        "attendees": [
            {
                "name": attendee's name,
                "href": URL to the attendee,
            },
            ...
        ]
    }
    """


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_attendee(request, id):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=id)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "conference" in content:
                conference = ConferenceVO.objects.get(id=["conference"])
                content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        Attendee.objects.filter(id=id).update(**content)

        attendee = Attendee.objects.get(id=id)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )

        #     {
        #         "email": attendee.email,
        #         "name": attendee.name,
        #         "company_name": attendee.company_name,
        #         "created": attendee.created,
        #         "conference": {
        #             "name": attendee.name,
        #             "href": attendee.get_api_url(),
        #         }
        #     }
        # )

