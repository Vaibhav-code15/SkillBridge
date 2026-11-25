from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_page(context, page_number):
    """Return the current query parameters with only the page value replaced."""
    query = context["request"].GET.copy()
    if "q" in query:
        query["q"] = query["q"].strip()
    query["page"] = page_number
    return query.urlencode()
