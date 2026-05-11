import django_filters

from .models import Location


class LocationFilter(django_filters.FilterSet):
    min_rating = django_filters.NumberFilter(field_name="avg_rating", lookup_expr="gte")
    max_rating = django_filters.NumberFilter(field_name="avg_rating", lookup_expr="lte")
    category = django_filters.ChoiceFilter(choices=Location.category.field.choices)

    class Meta:
        model = Location
        fields = ("category", "min_rating", "max_rating")
