import subprocess
import re
import sys


def get_package_dependencies(package_name, visited=None, graph_edges=None, level=0):
    """
    Получает зависимости пакета рекурсивно и создает граф.
    """
    if visited is None:
        visited = set()
    if graph_edges is None:
        graph_edges = set()

    if package_name in visited:
        return graph_edges

    visited.add(package_name)

    try:
        result = subprocess.run(
            ["apt", "show", package_name], capture_output=True, text=True, check=True
        )
        output = result.stdout
    except subprocess.CalledProcessError:
        print(f"Ошибка: Не удалось получить информацию о пакете: {package_name}")
        return graph_edges

    for line in output.splitlines():
        if line.startswith("Depends:"):
            dep_str = line[len("Depends:") :].strip()
            dep_list = re.split(r",\s*", dep_str)
            for dep in dep_list:
                dep_name = re.split(r"[\s(]", dep)[0]
                if dep_name != package_name:
                    graph_edges.add((package_name, dep_name))
                    get_package_dependencies(dep_name, visited, graph_edges, level + 1)
    return graph_edges


def generate_dot_file(package_name, graph_edges, filename="dependencies.dot"):
    """
    Генерирует DOT-файл на основе графа зависимостей.
    """
    with open(filename, "w") as f:
        f.write("digraph Dependencies {\n")
        f.write("  rankdir=LR;\n")
        for source, target in graph_edges:
            f.write(f'  "{source}" -> "{target}";\n')
        f.write("}\n")


def visualize_graph(
    dot_filename="dependencies.dot", output_filename="dependencies.png"
):
    """
    Визуализирует граф зависимостей с помощью Graphviz.
    """
    try:
        subprocess.run(
            ["dot", "-Tpng", dot_filename, "-o", output_filename], check=True
        )
        print(f"Граф зависимостей сохранен в {output_filename}")
    except FileNotFoundError:
        print(
            "Ошибка: Graphviz не установлен. Пожалуйста, установите его (например, 'sudo apt install graphviz')."
        )
    except subprocess.CalledProcessError:
        print("Ошибка: Не удалось сгенерировать изображение графа.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python script.py <имя_пакета>")
        sys.exit(1)

    package_name = sys.argv[1]
    graph_edges = get_package_dependencies(package_name)

    if graph_edges:
        generate_dot_file(package_name, graph_edges)
        visualize_graph()
    else:
        print(f"Пакет '{package_name}' не имеет зависимостей или не найден.")
