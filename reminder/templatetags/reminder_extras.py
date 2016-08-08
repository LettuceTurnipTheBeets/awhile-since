from django.template.defaulttags import register

# Custom Template Filters go here
@register.filter
def lookup(d, key):
    return d[key]

@register.simple_tag()
def total_count(local, parent, slice):
    if int(parent) == 0:
        offset = int(local)
    else:
        offset = int(slice[int(parent)-1].split(":")[1]) + int(local)

    return '{}'.format(offset)
