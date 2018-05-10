from django.template.defaulttags import register


@register.filter
def lookup(d, key):
    """Return the value of a dictionary"""
    return d[key]


@register.simple_tag()
def total_count(local, parent, slice):
    """Return the total count of a passed in time value"""
    if int(parent) == 0:
        offset = int(local)
    else:
        offset = int(slice[int(parent)-1].split(":")[1]) + int(local)

    return '{}'.format(offset)

