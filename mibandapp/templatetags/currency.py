from django import template

register = template.Library()

def currency(value):
    return '₦%s' % value

register.filter('currency', currency)

def savings(regular_price, sale_price):
    if regular_price > sale_price:
        return regular_price - sale_price
    else:
        return None
register.filter('savings', savings)

def total_cost(sale_price, quantity):
    return int(sale_price) * int(quantity)

register.filter('total_cost', total_cost)
