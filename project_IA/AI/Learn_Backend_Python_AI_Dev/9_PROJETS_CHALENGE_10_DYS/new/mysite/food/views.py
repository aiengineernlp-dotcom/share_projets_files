from tempfile import template
"""FONCTION/METHODS BASE ON VIEW IMPORTS"""
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.context_processors import request
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item
from .forms import ItemForm
from .models import Item
from django.template import loader
"""CLASS BASE ON VIEW IMPORTS"""
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView



# Create your views here.

"""FONCTION/METHODS BASE ON VIEW"""
def index(request):
    item_list = Item.objects.all() # je recupere les data dans la base de donnees grace au queryset
    context = {'item_list': item_list, } # je les charges dans le contexte pret a etre utiliser par le html
    template = loader.get_template('food/index.html') # je charge grace au loader le html qui recevra mes donnees
    return HttpResponse(template.render(context,request)) # je les retourne comme reponse a la requette via le templates html avec HttpResponse

def item(request):
    item_list = Item.objects.all()   # je recupere les data dans la base de donnees grace au queryset
    context ={'item_list': item_list,} # je les charges dans le contexte pret a etre utiliser par le html
    return render(request,'food/index.html',context) # je les retourne comme reponse a la requette via le templates html avec render

def detail(request,item_id):
    item = Item.objects.get(id=item_id)
    context = {'item': item,}   # attention au html oooooo
    return render(request,'food/detail.html',context)

def create_item(request):
    form = ItemForm(request.POST or None)
    #context={'form':form}
    if form.is_valid():
        form.save()
        return redirect('food:index')

    return render(request,'food/item-form.html',{'form':form})

def update_item(request, id):
    item = get_object_or_404(Item, id=id)  # Évite une erreur 500 si l'item n'existe pas
    #item = Item.objects.get(id=id)
    form = ItemForm(request.POST or None, instance=item)

    if form.is_valid():
        form.save()
        return redirect('food:index')

    return render(request, 'food/item-form.html', {'form': form, 'item': item})  # Fusion des dictionnaires

def delete_item(request, id):
    item = get_object_or_404(Item, id=id)  # Utilisation de get_object_or_404 pour éviter les erreurs

    if request.method == 'POST':  # Vérifie si la requête est une soumission de formulaire POST
        item.delete()  # Supprimer l'élément
        return redirect('food:index')  # Rediriger vers la liste des items après suppression

    return render(request, 'food/item-delete.html', {'item': item})  # Affiche la page de confirmation


"""CLASSes BASE ON VIEW"""
class IndexClassView(ListView):
    model = Item
    template_name ='food/index.html'
    context_object_name ='item_list'

class DetailClassView(DetailView):
    model = Item
    template_name = 'food/detail.html'

#moi
class CreateClasseBaseView(CreateView):
    model = Item
    fields  = ['item_name','item_des','item_price','item_image']
    template_name = 'food/item-form.html'

    def form_valid(self, form):
        form.instance.user_name = self.request.user
        return super().form_valid(form)


    context_object_name = 'form'


class Update_baseV_View(UpdateView):
    # model = Item
    # template_name =
    # context_object_name = ;
    pass

class Delete_baseV_View(DeleteView):
    # model = Item
    # template_name =
    # context_object_name = ;
    pass

