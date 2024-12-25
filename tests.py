import unittest
import subprocess
import os
import re
import sys
import io

# import mock если мы используем python < 3.8
try:
    from unittest import mock
except ImportError:
    import mock

from dependence_getter import (
    get_package_dependencies,
    generate_dot_file,
    visualize_graph,
)


class TestDependencyGraph(unittest.TestCase):
    def setUp(self):
        self.test_dot_file = "test_dependencies.dot"
        self.test_png_file = "test_dependencies.png"

    def tearDown(self):

        if os.path.exists(self.test_dot_file):
            os.remove(self.test_dot_file)
        if os.path.exists(self.test_png_file):
            os.remove(self.test_png_file)

    def test_get_package_dependencies_with_dependencies(self):
        dependencies = get_package_dependencies("python3")
        self.assertGreater(
            len(dependencies), 0
        )  # Проверяем, что есть хотя бы одна зависимость
        self.assertTrue(
            any("libc6" in dep for dep in dependencies)
        )  # Проверяем, что libc6 где-то есть в зависимостях

    def test_get_package_dependencies_no_dependencies(self):
        # Создадим фиктивный пакет без зависимостей
        # Если в системе есть пакет без зависимостей - можно использовать его
        dependencies = get_package_dependencies(
            "netbase"
        )  # Этот пакет в большинстве систем не имеет зависимостей, либо имеет но не всегда
        self.assertEqual(len(dependencies), 0)

    def test_get_package_dependencies_package_not_found(self):
        dependencies = get_package_dependencies("this_package_does_not_exist")
        self.assertEqual(len(dependencies), 0)

    def test_generate_dot_file(self):
        test_edges = {("package1", "package2"), ("package1", "package3")}
        generate_dot_file("test_package", test_edges, self.test_dot_file)
        self.assertTrue(os.path.exists(self.test_dot_file))
        with open(self.test_dot_file, "r") as f:
            content = f.read()
        self.assertIn("digraph Dependencies {", content)
        self.assertIn('"package1" -> "package2";', content)
        self.assertIn('"package1" -> "package3";', content)
        self.assertIn("rankdir=LR;", content)
        self.assertIn("}", content)

    def test_generate_dot_file_can_read_file(self):
        test_edges = {("package1", "package2"), ("package1", "package3")}
        generate_dot_file("test_package", test_edges, self.test_dot_file)
        self.assertTrue(os.path.exists(self.test_dot_file))
        try:
            with open(self.test_dot_file, "r") as f:
                f.read()
        except:
            self.fail("Файл не читается")

    def test_visualize_graph_success(self):
        # Создаем временный DOT-файл для теста
        test_edges = {("package1", "package2"), ("package1", "package3")}
        generate_dot_file("test_package", test_edges, self.test_dot_file)
        visualize_graph(self.test_dot_file, self.test_png_file)
        self.assertTrue(os.path.exists(self.test_png_file))

    def test_visualize_graph_graphviz_not_installed(self):
        # Сохраняем оригинальную функцию
        original_run = subprocess.run

        # Заменяем subprocess.run, чтобы выбросить исключение FileNotFoundError
        def mock_run(*args, **kwargs):
            if args[0][0] == "dot":
                raise FileNotFoundError("Mocked FileNotFoundError")
            return original_run(*args, **kwargs)

        subprocess.run = mock_run
        # Создаем временный DOT-файл для теста
        test_edges = {("package1", "package2"), ("package1", "package3")}
        generate_dot_file("test_package", test_edges, self.test_dot_file)
        # Перенаправляем вывод в переменную

        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            visualize_graph(self.test_dot_file, self.test_png_file)
            self.assertIn("Graphviz не установлен", stdout.getvalue())
        # Возвращаем оригинальную функцию subprocess.run
        subprocess.run = original_run


if __name__ == "__main__":
    unittest.main()
