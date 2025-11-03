"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from graphene_django.views import GraphQLView

from accounts.schema import schema as accounts_schema
from form.schema import schema as forms_schema
from conclusion.schema import schema as reports_schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('form/',include('form.urls')),

    path('graphql/accounts/', GraphQLView.as_view(graphiql=True, schema=accounts_schema)),
    path('graphql/form/', GraphQLView.as_view(graphiql=True, schema=forms_schema)),
    path('graphql/conclusion/', GraphQLView.as_view(graphiql=True, schema=reports_schema)),

]
