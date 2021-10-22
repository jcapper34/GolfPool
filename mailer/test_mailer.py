from mailer.postman import Postman
from picksets.pickset import Pickset
from players.player import Player


def test_picks_send():
    pickset = Pickset(
        name='John Capper',
        email='capperjohnm@gmail.com',
        pin=5753,
        picks=[
            [Player('32102', 'Rickie Fowler'), Player('32102', 'Rickie Fowler'), Player('32102', 'Rickie Fowler')],
            [Player('32102', 'Rickie Fowler'), Player('32102', 'Rickie Fowler'), Player('32102', 'Rickie Fowler')],
            [Player('32102', 'Rickie Fowler'), Player('32102', 'Rickie Fowler')],
            [Player('32102', 'Rickie Fowler'), Player('32102', 'Rickie Fowler')]
        ]
    )

    postman = Postman((pickset.email,))
    postman.make_picks_message(pickset.name, pickset.pin, pickset.picks)
    postman.send_message()