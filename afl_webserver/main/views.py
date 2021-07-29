from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,  
    UpdateView,
    DeleteView,
)
from . models import PVSystem

"""
Landing Page
"""
def dashboard(request):
    context ={
        "title": "Dashboard",
        "num_of_pv_systems": PVSystem.objects.count(),
        "num_of_error_logs": 17,
        "num_of_faults": 5,        
    }
    return render(request, 'main/dashboard.html', context)

"""
Create Views
"""
class PVSystemCreateView(CreateView):
    #form_class = PVSystemForm
    model = PVSystem

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add PV System'
        return context

"""
Detail Views
"""
class PVSystemDetailView(DetailView):
    model = PVSystem
    template_name = 'main/pvsystem_detail.html'

    def get_context_data(self, **kwargs):
        pv_system = PVSystem.objects.get(pk=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['title'] = pv_system.name
        return context

    
"""
List Views
"""
class PVSystemListView(ListView):
    model = PVSystem
    paginate_by = 50
    template_name = 'main/pvsystem_list.html'


"""
Update Views
"""
class PVSystemUpdateView(UpdateView):
    #form_class = PVSystemForm
    model = PVSystem

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pv_system = PVSystem.objects.get(pk=self.kwargs['pk'])
        context['title'] = f'Update {pv_system.name} details'
        return context

"""
Delete Views
"""
class PVSystemDeleteView(DeleteView):
    model = PVSystem
    success_url = reverse_lazy('pvsystems_list')