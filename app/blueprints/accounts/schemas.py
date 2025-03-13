from app.models import Account
from app.extensions import ma



class AccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Account

account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)