

class Service:
    secret = "test"
    def sum(self, a, b):
        result = a + b
        print("%s + %s = %s" % (a, b, result))