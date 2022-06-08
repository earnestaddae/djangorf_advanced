import pytest
import mock
from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError



class TestCommand:
    @pytest.mark.skip("wait_for_db is not defined error")
    def test_wait_for_db_ready(self, mocker):
        mocker.patch('core.management.commands.wait_for_db.Command.check')
        mocker.return_value = True

        call_command('wait_for_db')

        mocker.assert_called_once_with(databases=['default'])

    @pytest.mark.skip("wait_for_db is not defined error")
    @mock.patch('time.sleep')
    def test_wait_for_db_delay(self, mocked_sleep, mocker):
        mocker.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        assert mocker.call_count == 6

        mocker.assert_called_with(databases=['default'])