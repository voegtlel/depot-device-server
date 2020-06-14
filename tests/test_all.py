import time

from tests.test_api import TestApi


def test_open_bay():
    api = TestApi()
    assert not api.get_bay_open('bay1')
    api.post_open_bay('bay1')
    assert api.get_bay_open('bay1')
    time.sleep(11)
    assert not api.get_bay_open('bay1')


def test_card_id():
    api = TestApi()

    assert api.get_card_id().json['cardId'] is None

    from server import card_access

    card_access.insert_card('card1')

    assert api.get_card_id().json['cardId'] == 'card1'


if __name__ == '__main__':
    test_open_bay()
    test_card_id()
