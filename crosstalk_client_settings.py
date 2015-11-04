############
# SETTINGS #
############
# CROSSBAR_CLIENT_GETTER_TASKS = ['call_get_toppings_task', \
# 'call_get_all_toppings_task', 'call_get_drinks_task', 'call_find_by_phone_task', \
# 'call_get_cart_task', \
# 'call_add_customer_pizza_task']

#we are calling a function mainly to send data and save in database
CROSSBAR_CLIENT_SETTER_TASKS = [
{'cb_rpc': 'call_start_btm_process_task', 'result_global_var':'current_btm_process_id'},
{'cb_rpc': 'call_create_initial_buy_order_task', 'result_global_var':'None'},
]

#we are querying for objects to populate a kivy widget
CROSSBAR_CLIENT_WIDGET_GETTER_TASKS = [
{'cb_rpc': 'call_get_pizzas_task', 'kivy_widget':'PizzaWidget', 'kivy_widget_container': 'pizzas_container', 'txt_field': 'name'},
]

CROSSBAR_CLIENT_SUBSCRIPTIONS = [
{'cb_sub': 'CHF', 'widget': 'chfbuywidget'},
]


#{'cb_rpc': 'call_get_all_toppings_task', 'kivy_widget': 'PizzaToppingWidget', 'kivy_widget_container': 'pizza_toppings_container', 'txt_field': 'name'}

CROSSBAR_DOMAIN = 'com.example'


##getter task
#returns json result to populate a widget

##setter task
#creates something in backend, either no result or true on success

