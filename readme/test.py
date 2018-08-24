def person(name, age, **kw):
    print('name:', name, 'age:', age, 'other:', kw)
    mycity = kw.get('city')
    print(mycity)

person('Bob', 35, city='Beijing')


dict = {'Name': 'Zara', 'Age': 27}
print(dict.get())