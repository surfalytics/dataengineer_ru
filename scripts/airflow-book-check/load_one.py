"""Import one extracted block. DAG files go through DagBag, other files are executed as a module."""
import importlib.util, sys
from airflow.models import DagBag

path = sys.argv[1]
bag = DagBag(dag_folder=path)
if bag.import_errors:
    print(list(bag.import_errors.values())[0]); sys.exit(1)
if bag.dags:
    print("DAGs:", ", ".join(sorted(bag.dags)))
else:
    sys.path.insert(0, str(__import__("pathlib").Path(path).parent))
    spec = importlib.util.spec_from_file_location("block", path)
    spec.loader.exec_module(importlib.util.module_from_spec(spec))
    print("module ok")
