from pathlib import Path
from swimport.swim_run import swim_run_subfolders
from swimport.swim_run_paths import get_path_set

if __name__ == '__main__':
    # if things are compiling weird, first thing, change this to /Od
    optimization = '/O2'

    use_example_filters = True
    tests_dir = Path.cwd()

    if use_example_filters:
        from swimport.tests.resources.examples_filter import passes_filter
    else:
        from swimport.swim_run import simple_passes_filter as passes_filter

    swimport_paths = get_path_set()

    swim_run_subfolders(
        root_dir=tests_dir, optimization=optimization, passes_filter=passes_filter,
        print_out=True, swimport_paths=swimport_paths)
