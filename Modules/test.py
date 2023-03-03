class TEST:
    def test_method(self):
        var = 1
        print('test')


class TEST2(TEST):
    def test_method(self):
        super().test_method()
        print(var)


TEST2().test_method()