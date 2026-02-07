from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def get_filter_url(context, *args, **kwargs):
	filters = context["filters"].copy()

	if "dir" in args:
		filters["direction"] = "asc" if filters["direction"] == "desc" else "desc"
	for key, value in kwargs.items():
		filters[key] = value
	return f"?{urlencode(filters)}"