import os.path
from datetime import datetime
from unittest import TestCase

from mock_alchemy.mocking import UnifiedAlchemyMagicMock

from db.models import EtfHistory
from etf_history import get_isin_dict, write_history_to_db


class TestEtfHistory(TestCase):

    def test_get_isin_dict(self):
        res = get_isin_dict(os.path.join('../docs', 'examples'))

        assert len(res) == 4
        assert res['ISHARES ATX (DE)'] == 'DE000A0D8Q23'

    def test_get_etf_history(self):
        session = UnifiedAlchemyMagicMock()
        write_history_to_db(os.path.join('../docs', 'examples'), session)

        # querying for further data will fail due to limitations of this mock
        date = datetime.strptime('01.02.2021', '%d.%m.%Y').date()
        res: EtfHistory = session.query(EtfHistory).filter_by(isin='DE000A0D8Q23', datapoint_date=date).first()
        assert res.price == 31.84
        assert res.price_index == 84.7
        assert res.return_index == 110.01
