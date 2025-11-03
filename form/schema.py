import graphene
from graphene_django import DjangoObjectType
from .models import Category, Form, Process, Answer

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "create", "update", "forms")

class FormType(DjangoObjectType):
    class Meta:
        model = Form
        fields = ("id", "title", "question", "description", "type", "options", "category", "processes", "answers")

class ProcessType(DjangoObjectType):
    class Meta:
        model = Process
        fields = ("id", "name", "forms", "liner", "password", "view_count", "answers")

class AnswerType(DjangoObjectType):
    class Meta:
        model = Answer
        fields = ("id", "process", "form", "type", "answer")

class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    all_forms = graphene.List(FormType)
    all_processes = graphene.List(ProcessType)
    all_answers = graphene.List(AnswerType)

    def resolve_all_categories(root, info):
        return Category.objects.all()
    def resolve_all_forms(root, info):
        return Form.objects.all()
    def resolve_all_processes(root, info):
        return Process.objects.all()
    def resolve_all_answers(root, info):
        return Answer.objects.all()

class CreateCategory(graphene.Mutation):
    category = graphene.Field(CategoryType)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)

    def mutate(self, info, name, description):
        category = Category(name=name, description=description)
        category.save()
        return CreateCategory(category=category)

class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
