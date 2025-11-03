import graphene
from graphene_django import DjangoObjectType
from .models import ReportSubscription, FormReport

class ReportSubscriptionType(DjangoObjectType):
    class Meta:
        model = ReportSubscription
        fields = ("id", "form", "email", "interval", "last_sent", "created_at")

class FormReportType(DjangoObjectType):
    class Meta:
        model = FormReport
        fields = ("id", "form", "view_count", "answer_count", "summary", "updated_at")

class Query(graphene.ObjectType):
    all_subscriptions = graphene.List(ReportSubscriptionType)
    all_form_reports = graphene.List(FormReportType)

    def resolve_all_subscriptions(root, info):
        return ReportSubscription.objects.all()

    def resolve_all_form_reports(root, info):
        return FormReport.objects.all()

class Mutation(graphene.ObjectType):
    pass 

schema = graphene.Schema(query=Query, mutation=Mutation)
