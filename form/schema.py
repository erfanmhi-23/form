import graphene
from graphene_django import DjangoObjectType
from .models import Category, Form, Process, Answer, ProcessForm
from accounts.models import User


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"


class FormType(DjangoObjectType):
    class Meta:
        model = Form
        fields = "__all__"


class ProcessFormType(DjangoObjectType):
    class Meta:
        model = ProcessForm
        fields = "__all__"


class ProcessType(DjangoObjectType):
    class Meta:
        model = Process
        fields = "__all__"

    process_forms = graphene.List(ProcessFormType)

    def resolve_process_forms(self, info):
        return self.processform_set.all().order_by("order")


class AnswerType(DjangoObjectType):
    class Meta:
        model = Answer
        fields = "__all__"

class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    category_by_id = graphene.Field(CategoryType, id=graphene.Int(required=True))

    all_forms = graphene.List(FormType)
    form_by_id = graphene.Field(FormType, id=graphene.Int(required=True))

    all_processes = graphene.List(ProcessType)
    process_by_id = graphene.Field(ProcessType, id=graphene.Int(required=True))

    all_answers = graphene.List(AnswerType)
    answers_by_user = graphene.List(AnswerType, user_id=graphene.Int(required=True))

    def resolve_all_categories(root, info):
        return Category.objects.all()

    def resolve_category_by_id(root, info, id):
        return Category.objects.get(pk=id)

    def resolve_all_forms(root, info):
        return Form.objects.all()

    def resolve_form_by_id(root, info, id):
        return Form.objects.get(pk=id)

    def resolve_all_processes(root, info):
        return Process.objects.all()

    def resolve_process_by_id(root, info, id):
        return Process.objects.get(pk=id)

    def resolve_all_answers(root, info):
        return Answer.objects.all()

    def resolve_answers_by_user(root, info, user_id):
        return Answer.objects.filter(user_id=user_id)


schema = graphene.Schema(query=Query)
