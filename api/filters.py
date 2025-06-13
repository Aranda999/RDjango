import django_filters
from api.models import Reservacion,SalaJuntas
from datetime import timedelta
from datetime import datetime
from django.contrib.auth.models import User

class ReservacionFilter(django_filters.FilterSet):
    fecha = django_filters.DateFilter(field_name='fecha', lookup_expr='exact')
    sala = django_filters.ModelChoiceFilter(queryset=SalaJuntas.objects.all())
    evento = django_filters.CharFilter(field_name='evento', lookup_expr='icontains')
    usuario = django_filters.ModelChoiceFilter(queryset=User.objects.all(), field_name='usuario')

    class Meta:
        model = Reservacion
        fields = ['fecha', 'sala', 'evento', 'usuario']


class GraficoFilter(django_filters.FilterSet):
    periodo = django_filters.ChoiceFilter(choices=[
        ('semana', 'Semana'),
        ('mes', 'Mes'),
        ('año', 'Año')
    ], method='filter_periodo')

    class Meta:
        model = Reservacion
        fields = []

    def filter_periodo(self, queryset, name, value):
        if value == 'semana':
            return queryset.filter(fecha__gte=datetime.now() - timedelta(days=7))
        elif value == 'mes':
            return queryset.filter(fecha__gte=datetime.now() - timedelta(days=30))
        elif value == 'año':
            return queryset.filter(fecha__gte=datetime.now() - timedelta(days=365))
        return queryset