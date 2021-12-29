from mailer.postman import Postman
from picksets.pickset import Pickset
from players.player import Player


def test_picks_send():
    pickset = Pickset(
        name='John Capper',
        email='capperjohnm@gmail.com',
        pin=5753,
        picks= [
            (Player(id='32102', name='Rickie Fowler'), Player(id='32102', name='Rickie Fowler'), Player(id='32102', name='Rickie Fowler')),
            (Player(id='32102', name='Rickie Fowler'), Player(id='32102', name='Rickie Fowler'), Player(id='32102', name='Rickie Fowler')),
            (Player(id='32102', name='Rickie Fowler'), Player(id='32102', name='Rickie Fowler')),
            (Player(id='32102', name='Rickie Fowler'), Player(id='32102', name='Rickie Fowler'))
        ]
    )

    postman = Postman((pickset.email,))
    postman.make_picks_message(pickset.name, pickset.pin, pickset.picks)
    postman.send_message()