from subprocess import call
import sys
sys.path.append('../')
from inspect_terminals import config
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def generate_mysql_models_two(
        connector: str,
        filename: str
        ) -> None:
    connection_string = str(connector)
    output_file = f"{filename}.py"

    call(f"sqlacodegen {connection_string} > {current_dir}/{output_file}", shell=True)


def generate_mysql_models_three(
        connector: str,
        filename: str
        ) -> None:
    connection_string = str(connector)
    output_file = f"{filename}.py"

    call(f"sqlacodegen {connection_string} > {current_dir}/{output_file}", shell=True)

if __name__ == "__main__":
    generate_mysql_models_two(
        connector=str(config.connection_mysql),
        filename="mysql_models_two"
    )
