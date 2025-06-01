from unittest.mock import MagicMock, mock_open, patch

from src.file_operations.file_operations import (read_operations_from_csv,
                                                 read_operations_from_excel)


def test_read_operations_from_csv_success_mock():
    """Тест успешного чтения операций из CSV с использованием mock."""
    mock_file = mock_open(read_data="id,amount,description\n1,100,Test 1\n2,200,Test 2\n")
    with patch('builtins.open', mock_file):
        operations = read_operations_from_csv('dummy_path.csv')
        expected_operations = [
            {'id': '1', 'amount': '100', 'description': 'Test 1'},
            {'id': '2', 'amount': '200', 'description': 'Test 2'}
        ]
        assert operations == expected_operations


def test_read_operations_from_csv_empty_file_mock():
    """Тест чтения пустого CSV-файла с использованием mock."""
    mock_file = mock_open(read_data="")
    with patch('builtins.open', mock_file):
        operations = read_operations_from_csv('dummy_path.csv')
        assert operations == []


def test_read_operations_from_csv_no_header_mock():
    """Тест чтения CSV-файла без заголовка с использованием mock."""
    mock_file = mock_open(read_data="value1,value2\nvalue3,value4\n")
    with patch('builtins.open', mock_file):
        operations = read_operations_from_csv('dummy_path.csv')
        assert operations == [{'value1': 'value3', 'value2': 'value4'}]


def test_read_operations_from_csv_file_not_found_mock():
    """Тест чтения несуществующего CSV-файла с использованием mock."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        operations = read_operations_from_csv('non_existent.csv')
        assert operations == []


def test_read_operations_from_excel_success_mock():
    """Тест успешного чтения операций из Excel с использованием mock."""
    mock_workbook = MagicMock()
    mock_sheet = mock_workbook.active
    mock_sheet.max_row = 3
    mock_sheet.__getitem__.side_effect = [
        [MagicMock(value='id'), MagicMock(value='amount'), MagicMock(value='description')],
        [MagicMock(value=1), MagicMock(value=100), MagicMock(value='Test 1')],
        [MagicMock(value=2), MagicMock(value=200), MagicMock(value='Test 2')]
    ]
    with patch('openpyxl.load_workbook', return_value=mock_workbook):
        operations = read_operations_from_excel('dummy_path.xlsx')
        expected_operations = [
            {'id': 1, 'amount': 100, 'description': 'Test 1'},
            {'id': 2, 'amount': 200, 'description': 'Test 2'}
        ]
        assert operations == expected_operations


def test_read_operations_from_excel_empty_file_mock():
    """Тест чтения пустого Excel-файла с использованием mock."""
    mock_workbook = MagicMock()
    mock_sheet = mock_workbook.active
    mock_sheet.max_row = 1
    mock_sheet.__getitem__.return_value = [None, None, None]
    with patch('openpyxl.load_workbook', return_value=mock_workbook):
        operations = read_operations_from_excel('dummy_path.xlsx')
        assert operations == []


def test_read_operations_from_excel_no_header_mock():
    """Тест чтения Excel-файла без заголовка с использованием mock."""
    mock_workbook = MagicMock()
    mock_sheet = mock_workbook.active
    mock_sheet.max_row = 2
    mock_sheet.__getitem__.side_effect = [
        [MagicMock(value=None), MagicMock(value=None), MagicMock(value=None)],
        [MagicMock(value=1), MagicMock(value=100), MagicMock(value='Test 1')]
    ]
    with patch('openpyxl.load_workbook', return_value=mock_workbook):
        operations = read_operations_from_excel('dummy_path.xlsx')
        assert operations == []


def test_read_operations_from_excel_file_not_found_mock():
    """Тест чтения несуществующего Excel-файла с использованием mock."""
    with patch('openpyxl.load_workbook', side_effect=FileNotFoundError):
        operations = read_operations_from_excel('non_existent.xlsx')
        assert operations == []
