from django.test import TestCase

from general.views import MultipleSystemsEstimation


class TestMseView(TestCase):
    """Test the MultipleSystemsEstimation view."""

    def test__calculate_initial_data_with_3(self):
        """Test the input table data creation process with 3 lists."""
        expected = (
            ['list 1', 'list 2', 'list 3'],
            [
                {'required_lists': ['list 1'], 'first': False},
                {'required_lists': ['list 2'], 'first': False},
                {'required_lists': ['list 3'], 'first': False},
                {'required_lists': ['list 1', 'list 2'], 'first': True},
                {'required_lists': ['list 1', 'list 3'], 'first': False},
                {'required_lists': ['list 2', 'list 3'], 'first': False},
                {'required_lists': ['list 1', 'list 2', 'list 3'], 'first': True},
            ]
        )
        result = MultipleSystemsEstimation()._calculate_initial_data(3)
        self.assertEqual(result, expected)

    def test__calculate_initial_data_with_4(self):
        """Test the input table data creation process with 4 lists."""
        expected = (
            ['list 1', 'list 2', 'list 3', 'list 4'],
            [
                {'required_lists': ['list 1'], 'first': False},
                {'required_lists': ['list 2'], 'first': False},
                {'required_lists': ['list 3'], 'first': False},
                {'required_lists': ['list 4'], 'first': False},
                {'required_lists': ['list 1', 'list 2'], 'first': True},
                {'required_lists': ['list 1', 'list 3'], 'first': False},
                {'required_lists': ['list 1', 'list 4'], 'first': False},
                {'required_lists': ['list 2', 'list 3'], 'first': False},
                {'required_lists': ['list 2', 'list 4'], 'first': False},
                {'required_lists': ['list 3', 'list 4'], 'first': False},
                {'required_lists': ['list 1', 'list 2', 'list 3'], 'first': True},
                {'required_lists': ['list 1', 'list 2', 'list 4'], 'first': False},
                {'required_lists': ['list 1', 'list 3', 'list 4'], 'first': False},
                {'required_lists': ['list 2', 'list 3', 'list 4'], 'first': False},
                {'required_lists': ['list 1', 'list 2', 'list 3', 'list 4'], 'first': True},
            ]
        )
        result = MultipleSystemsEstimation()._calculate_initial_data(4)
        self.assertEqual(result, expected)
