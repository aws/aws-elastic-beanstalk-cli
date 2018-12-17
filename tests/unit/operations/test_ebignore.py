# -*- coding: UTF-8 -*-

import os
import shutil
import sys

import unittest
from mock import patch

from ebcli.core import fileoperations


class TestEbIgnore(unittest.TestCase):

    def setUp(self):
        os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        parent_dir = os.path.dirname(os.getcwd())
        os.chdir(parent_dir)
        shutil.rmtree('testDir')

    @patch('ebcli.core.fileoperations.get_project_root')
    @patch('ebcli.core.fileoperations.get_ebignore_location')
    def test_get_ebignore_list__includes_dotted_files_in_the_ebignore_list(
            self,
            get_ebignore_location_mock,
            get_project_root_mock
    ):
        get_project_root_mock.return_value = os.getcwd()
        get_ebignore_location_mock.return_value = os.path.join(os.getcwd(), '.ebignore')

        os.mkdir('directory_1')
        open('.gitignore', 'w').close()
        open('.dotted_file', 'w').close()
        open('directory_1{}.dotted_file'.format(os.path.sep), 'w').close()

        with open('.ebignore', 'w') as file:
            ebignore_file_contents = """
# ignore special dot file
.gitignore

# ignore dot file
.dotted_file

# ignore inner-level dot file'
directory_1/.dotted_file
"""

            file.write(ebignore_file_contents)
            file.close()

        paths_to_ignore = fileoperations.get_ebignore_list()

        self.assertEqual(
            {
                '.gitignore',
                '.dotted_file',
                'directory_1{}.dotted_file'.format(os.path.sep),
                '.ebignore'
            },
            set(paths_to_ignore)
        )

    @patch('ebcli.core.fileoperations.get_project_root')
    @patch('ebcli.core.fileoperations.get_ebignore_location')
    def test_get_ebignore_list__includes_regular_files_in_the_ebignore_list(
            self,
            get_ebignore_location_mock,
            get_project_root_mock
    ):
        get_project_root_mock.return_value = os.getcwd()
        get_ebignore_location_mock.return_value = os.path.join(os.getcwd(), '.ebignore')

        os.mkdir('directory_1')
        open('file_1', 'w').close()
        open('directory_1/file_2', 'w').close()
        open('directory_1/file_3', 'w').close()

        with open('.ebignore', 'w') as file:
            ebignore_file_contents = """
# ignore regular top-level file
file_1

# ignore regular inner-level file'
directory_1/file_2
""".format(os.path.sep)

            file.write(ebignore_file_contents)
            file.close()

        paths_to_ignore = fileoperations.get_ebignore_list()

        self.assertEqual(
            {'file_1', 'directory_1{}file_2'.format(os.path.sep), '.ebignore'},
            set(paths_to_ignore)
        )

    @patch('ebcli.core.fileoperations.get_project_root')
    @patch('ebcli.core.fileoperations.get_ebignore_location')
    def test_get_ebignore_list__includes_directories_in_the_ebignore_list(
            self,
            get_ebignore_location_mock,
            get_project_root_mock
    ):
        get_project_root_mock.return_value = os.getcwd()
        get_ebignore_location_mock.return_value = os.path.join(os.getcwd(), '.ebignore')

        os.mkdir('directory_1')
        open('directory_1{}.gitkeep'.format(os.path.sep), 'w').close()
        os.mkdir('directory_2')
        open('directory_2{}.gitkeep'.format(os.path.sep), 'w').close()

        with open('.ebignore', 'w') as file:
            ebignore_file_contents = """
# ignore regular top-level file
directory_1

# ignore regular inner-level file
directory_2/
"""

            file.write(ebignore_file_contents)
            file.close()

        paths_to_ignore = fileoperations.get_ebignore_list()

        self.assertEqual(
            {
                'directory_1{}.gitkeep'.format(os.path.sep),
                'directory_2{}.gitkeep'.format(os.path.sep),
                '.ebignore'
            },
            set(paths_to_ignore)
        )

    @patch('ebcli.core.fileoperations.get_project_root')
    @patch('ebcli.core.fileoperations.get_ebignore_location')
    def test_get_ebignore_list__excludes_paths_escaped_with_exclamation_from_the_ebignore_list(
            self,
            get_ebignore_location_mock,
            get_project_root_mock
    ):
        get_project_root_mock.return_value = os.getcwd()
        get_ebignore_location_mock.return_value = os.path.join(os.getcwd(), '.ebignore')

        os.mkdir('directory_1')
        os.mkdir(os.path.join('directory_1', 'directory_2'))
        open('directory_1{0}file_1'.format(os.path.sep), 'w').close()
        open('directory_1{0}file_2'.format(os.path.sep), 'w').close()
        open('directory_1{0}directory_2{0}file_1'.format(os.path.sep), 'w').close()
        open('directory_1{0}directory_2{0}file_2'.format(os.path.sep), 'w').close()

        with open('.ebignore', 'w') as file:
            ebignore_file_contents = """
# ignore top-level directory and all its contents
directory_1/*

# exclude a directory inside the above
!directory_1/directory_2

# ignore the contents of the inner directory
directory_1/directory_2/*

# exclude the file of inside the inner directory that you want to commit to VC
!directory_1/directory_2/file_2
"""

            file.write(ebignore_file_contents)
            file.close()

        paths_to_ignore = fileoperations.get_ebignore_list()

        self.assertEqual(
            {
                'directory_1{0}file_1'.format(os.path.sep),
                'directory_1{0}file_2'.format(os.path.sep),
                'directory_1{0}directory_2{0}file_1'.format(os.path.sep),
                '.ebignore'
            },
            set(paths_to_ignore)
        )

    @patch('ebcli.core.fileoperations.get_project_root')
    @patch('ebcli.core.fileoperations.get_ebignore_location')
    def test_get_ebignore_list__includes_filenames_with_spaces_in_ignore_list(
            self,
            get_ebignore_location_mock,
            get_project_root_mock
    ):
        get_project_root_mock.return_value = os.getcwd()
        get_ebignore_location_mock.return_value = os.path.join(os.getcwd(), '.ebignore')

        open('file 1', 'w').close()

        with open('.ebignore', 'w') as file:
            ebignore_file_contents = """
file\ 1
"""

            file.write(ebignore_file_contents)
            file.close()

        paths_to_ignore = fileoperations.get_ebignore_list()

        self.assertEqual(
            {'file 1', '.ebignore'},
            set(paths_to_ignore)
        )

    @patch('ebcli.core.fileoperations.get_project_root')
    @patch('ebcli.core.fileoperations.get_ebignore_location')
    def test_get_ebignore_list__includes_filenames_with_exclamations_in_ignore_list(
            self,
            get_ebignore_location_mock,
            get_project_root_mock
    ):
        get_project_root_mock.return_value = os.getcwd()
        get_ebignore_location_mock.return_value = os.path.join(
            os.getcwd(), '.ebignore')

        open('!file_1', 'w').close()

        with open('.ebignore', 'w') as file:
            ebignore_file_contents = """
\!file_1
"""

            file.write(ebignore_file_contents)
            file.close()

        paths_to_ignore = fileoperations.get_ebignore_list()

        self.assertEqual(
            {'!file_1', '.ebignore'},
            set(paths_to_ignore)
        )

    @unittest.skipIf(sys.version_info < (3, 0), reason='Python 2.7.x does not support non-ASCII characters')
    @unittest.skipIf(sys.platform.startswith('darwin'), reason='OS X related problem')
    @patch('ebcli.core.fileoperations.get_project_root')
    @patch('ebcli.core.fileoperations.get_ebignore_location')
    def test_get_ebignore_list__includes_files_with_unicode_names(
            self,
            get_ebignore_location_mock,
            get_project_root_mock
    ):
        get_project_root_mock.return_value = os.getcwd()
        get_ebignore_location_mock.return_value = os.path.join(os.getcwd(), '.ebignore')

        open('哈哈', 'w').close()
        open('昨夜のコンサートは最高でした。', 'w').close()
        open('ändrar något i databasen', 'w').close()

        with open('.ebignore', 'wb') as file:
            ebignore_file_contents = """
哈哈
昨夜のコンサートは最高でした。
ändrar\ något\ i\ databasen
"""

            file.write(ebignore_file_contents.encode("UTF-8"))
            file.close()

        paths_to_ignore = fileoperations.get_ebignore_list()

        self.assertEqual(
            {'哈哈', '昨夜のコンサートは最高でした。', 'ändrar något i databasen', '.ebignore'},
            set(paths_to_ignore)
        )
