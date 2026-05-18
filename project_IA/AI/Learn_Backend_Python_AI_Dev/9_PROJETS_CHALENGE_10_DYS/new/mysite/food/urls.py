from . import views
from django.urls import path


app_name = 'food'
urlpatterns = [
    #/food/
    path ('',views.IndexClassView.as_view(),name= 'index'),

    path('item/',views.item,name='item'),
    #food/1
    path ('<int:pk>/',views.DetailClassView.as_view(),name='detail'),
    #add items --- Fonction base on view
    path('add/',views.create_item, name= "create_item"),
    # add items --- Classe base on view
    # path('add/',views.CreateClasseBaseView.as_view(), name= "create_item"),
    # edit
    path('update/<int:id>/', views.update_item, name='update_item'),
    #delete
    path('delete/<int:id>/', views.delete_item, name="delete_item"),  # Notez la barre oblique ici

]
