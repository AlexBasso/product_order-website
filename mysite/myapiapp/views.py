from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from .serializers import GroupSerializer
from rest_framework.mixins import ListModelMixin, CreateModelMixin

@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({"message": "Hello World!"})


class GroupsListView(ListCreateAPIView): # or (ListModelMixin, GenericAPIView)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get(self, request: Request) -> Response:
        return self.list(request)


# class GroupsListView(APIView):
#     def get(self, request: Request) -> Response:
#         groups = Group.objects.all()
#         serialized = GroupSerializer(groups, many=True)
#         return Response({"groups": serialized.data})


# class GroupsListView(APIView):
#     def get(self, request: Request) -> Response:
#         groups = Group.objects.all()
#         data = [group.name for group in groups]
#         return Response({"groups": data})