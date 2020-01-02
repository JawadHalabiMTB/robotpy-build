import argparse
import glob
from os.path import basename, exists, join, relpath, splitext

from .setup import Setup
from .generator_data import MissingReporter


class GenCreator:
    @classmethod
    def add_subparser(cls, parent_parser, subparsers):
        parser = subparsers.add_parser(
            "create-gen",
            help="Create YAML files from parsed header files",
            parents=[parent_parser],
        )
        parser.add_argument(
            "--write", help="Write to files if they don't exist", action="store_true"
        )

        parser.set_defaults(cls=cls)

    def run(self, s: Setup, args):

        for wrapper in s.wrappers:
            reporter = MissingReporter()
            wrapper.on_build_gen("", reporter)

            nada = True
            for name, report in reporter.as_yaml():
                nada = False
                if args.write:
                    if not exists(name):
                        print("Writing", name)
                        with open(name, "w") as fp:
                            fp.write(report)
                    else:
                        print(name, "already exists!")

                print("===", name, "===")
                print(report)

            if nada:
                print("Nothing to do!")


class HeaderScanner:
    @classmethod
    def add_subparser(cls, parent_parser, subparsers):
        parser = subparsers.add_parser(
            "scan-headers",
            help="Generate a list of headers in TOML form",
            parents=[parent_parser],
        )
        parser.set_defaults(cls=cls)

    def run(self, s: Setup, args):
        for wrapper in s.wrappers:
            for incdir in wrapper.get_include_dirs():
                files = list(
                    sorted(
                        relpath(f, incdir) for f in glob.glob(join(incdir, "**", "*.h"))
                    )
                )

                print("generate = [")
                for f in files:
                    if "rpygen" not in f:
                        base = splitext(basename(f))[0]
                        print(f'    {{ {base} = "{f}" }},')
                print("]")


def main():

    parser = argparse.ArgumentParser(prog="robotpy-build")
    parent_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    GenCreator.add_subparser(parent_parser, subparsers)
    HeaderScanner.add_subparser(parent_parser, subparsers)

    args = parser.parse_args()
    cmd = args.cls()

    s = Setup()
    s.prepare()
    retval = cmd.run(s, args)

    if retval is False:
        retval = 1
    elif retval is True:
        retval = 0
    elif isinstance(retval, int):
        pass
    else:
        retval = 0

    exit(retval)
