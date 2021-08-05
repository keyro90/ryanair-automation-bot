from unittest import TestCase

from tours.AutoreisenNavigation import AutoreisenNavigation


class TestAutoreisenNavigation(TestCase):

    def test_run(self):
        au = AutoreisenNavigation("Tenerife-South", "Same office", "2021-12-09 18:00", "2021-12-23 19:00",
                                  "../geckodriver", False)
        res = au.run()
        print(res)
