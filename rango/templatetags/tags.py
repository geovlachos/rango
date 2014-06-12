from django import template
register = template.Library()

@register.simple_tag
def active(request, pattern):
    if request.path == pattern:
        return 'active'
    return ''

@register.filter
def field_type(field):
    type = field.field.widget.__class__.__name__
    if type is 'TextInput':
        return 'text'
    elif type is 'PasswordInput':
        return 'password'
    elif type is 'EmailInput':
        return 'email'
    elif type is 'URLInput':
        return 'url'
    elif type is 'ClearableFileInput':
        return 'file'
    else:
        return type
