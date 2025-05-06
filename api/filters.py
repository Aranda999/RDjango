import django_filters
from api.models import Reservacion,SalaJuntas

class ReservacionFilter(django_filters.FilterSet):
    fecha = django_filters.DateFilter(field_name='fecha', lookup_expr='exact')
    sala = django_filters.ModelChoiceFilter(queryset=SalaJuntas.objects.all())
    evento = django_filters.CharFilter(field_name='evento', lookup_expr='icontains')

    class Meta:
        model = Reservacion
        fields = ['fecha', 'sala', 'evento']