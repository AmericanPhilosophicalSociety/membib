from datetime import datetime
from django.test import TestCase
import pytest
from django.core.exceptions import ValidationError

from .models import validate_year, verify_latlon


class TestValidators(TestCase):
    def test_year_is_valid(self):
        """Test whether validate_year raises correct exceptions"""
        current_year = datetime.now().year
        # valid
        validate_year(1743)
        # valid
        validate_year(current_year)

        with pytest.raises(ValidationError) as excinfo:
            validate_year(600)
        assert '600 does not match the expected date scope for this project' in str(
            excinfo.value
        )

        with pytest.raises(ValidationError) as excinfo:
            next_year = current_year + 1
            validate_year(next_year)
        assert (
            f'{next_year} does not match the expected date scope for this project'
            in str(excinfo.value)
        )

    def test_lat_lon_is_valid(self):
        """Test whether lat/long validation errors are raised"""

        # valid
        verify_latlon(52.520008)
        # valid
        verify_latlon(-75.1652)

        with pytest.raises(ValidationError) as excinfo:
            verify_latlon(-181.35214)
        assert 'Latitude or longitude must be between -180 and 180 degrees.' in str(
            excinfo.value
        )

        with pytest.raises(ValidationError) as excinfo:
            verify_latlon(181.35214)
        assert 'Latitude or longitude must be between -180 and 180 degrees.' in str(
            excinfo.value
        )
