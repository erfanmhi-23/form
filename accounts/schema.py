import graphene
from graphene_django import DjangoObjectType
from .models import User, EmailOTP
from django.contrib.auth import get_user_model

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "phone_number", "sex")

class EmailOTPType(DjangoObjectType):
    class Meta:
        model = EmailOTP
        fields = ("id", "email", "code", "created_at", "is_used")

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.Int(required=True))
    all_otps = graphene.List(EmailOTPType)

    def resolve_all_users(root, info):
        return get_user_model().objects.all()

    def resolve_user_by_id(root, info, id):
        return get_user_model().objects.get(pk=id)

    def resolve_all_otps(root, info):
        return EmailOTP.objects.all()

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        phone_number = graphene.String()
        sex = graphene.Boolean()

    def mutate(self, info, username, email, password, phone_number=None, sex=None):
        user = get_user_model()(username=username, email=email, phone_number=phone_number, sex=sex)
        user.set_password(password)
        user.save()
        return CreateUser(user=user)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
