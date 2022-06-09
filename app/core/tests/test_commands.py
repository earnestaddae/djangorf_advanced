import pytest
import mock
from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError

pytestmark = pytest.mark.django_db


class TestCommand:

    @pytest.mark.skip
    def test_wait_for_db_ready(self, mocker):
        mk = mocker.Mock()
        mk.patch('core.management.commands.wait_for_db.Command.check')
        mk.return_value = True

        call_command('wait_for_db')

        mk.assert_called_once_with(databases=['default'])


    @pytest.mark.skip
    @mock.patch('time.sleep')
    def test_wait_for_db_delay(self, mocked_sleep, mocker):
        mk = mocker.Mock()
        mk.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        assert mk.call_count == 6

        mk.assert_called_with(databases=['default'])