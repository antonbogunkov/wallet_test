import factory

from .models import Wallet, Transaction


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wallet

    label = factory.Sequence(lambda n: f"Wallet {n}")
    balance = factory.Faker(
        "pydecimal",
        min_value=0,
        max_value=9999.999999999999999999,
    )


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    wallet = factory.SubFactory(WalletFactory)
    txid = factory.Faker("uuid4")
    amount = factory.Faker(
        "pydecimal",
        min_value=-99.999999999999999999,
        max_value=99.999999999999999999,
    )
