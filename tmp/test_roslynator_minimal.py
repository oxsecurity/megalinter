import json
import os
import sys
import types
import importlib.util


# Create a lightweight dummy 'megalinter' module so we can import the Roslynator linter
# without pulling the full project dependencies (yaml, etc.).
megalinter_mod = types.ModuleType("megalinter")


class DummyLinter:
    def __init__(self, params=None, linter_config=None):
        self.request_id = params.get("request_id") if params else None
        self.report_folder = None
        self.workspace = None
        self.sarif_output_file = None
        self.name = None
        self.linter_url = "https://github.com/dotnet/Roslynator"

    def get_linter_version(self):
        return "0.0.0"

    def execute_lint_command(self, cmd):
        return (0, "")

    def process_linter(self, file=None):
        return None


megalinter_mod.Linter = DummyLinter

# Minimal dummy utils used by RoslynatorLinter during tests
dummy_utils = types.ModuleType("megalinter.utils")

def _can_write_report_files(master):
    return True

def _normalize_log_string(s):
    return s

dummy_utils.can_write_report_files = _can_write_report_files
dummy_utils.normalize_log_string = _normalize_log_string

megalinter_mod.utils = dummy_utils

# Inject into sys.modules so subsequent imports find it
sys.modules["megalinter"] = megalinter_mod

# Load RoslynatorLinter by file so it uses our dummy megalinter module
rl_path = os.path.join(os.path.dirname(__file__), os.pardir, "megalinter", "linters", "RoslynatorLinter.py")
rl_path = os.path.normpath(rl_path)
spec = importlib.util.spec_from_file_location("roslynator_module", rl_path)
ros_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ros_mod)

RoslynatorLinter = getattr(ros_mod, "RoslynatorLinter")


def main():
    tmpdir = "tmp_test_roslynator"
    os.makedirs(tmpdir, exist_ok=True)

    json_report = os.path.join(tmpdir, "roslynator_report.json")
    xml_report = os.path.join(tmpdir, "roslynator_report.xml")

    # sample JSON report
    sample_json = {
        "diagnostics": [
            {"id": "R001", "message": "Example issue", "file": "src/foo.cs", "line": 10}
        ]
    }
    with open(json_report, "w", encoding="utf-8") as fh:
        json.dump(sample_json, fh)

    # sample XML report
    sample_xml = """<?xml version='1.0'?>
<reports>
  <diagnostic>
    <id>R002</id>
    <message>XML issue</message>
    <file>src/bar.cs</file>
    <line>20</line>
  </diagnostic>
</reports>
"""
    with open(xml_report, "w", encoding="utf-8") as fh:
        fh.write(sample_xml)

    # Instantiate linter using dummy Linter base
    linter = RoslynatorLinter(params={"request_id": "test"}, linter_config={})
    linter.report_folder = tmpdir
    linter.workspace = tmpdir
    linter.name = "CSHARP_ROSLYNATOR"
    # Provide minimal runtime attributes expected by reporter helper
    linter.stdout = ""
    linter.master = types.SimpleNamespace(report_folder=tmpdir, request_id="test")

    print("Testing JSON report conversion:")
    sarif_json = linter._convert_report_to_sarif(json_report)
    print(json.dumps(sarif_json, indent=2, ensure_ascii=False))

    print("\nTesting XML report conversion:")
    sarif_xml = linter._convert_report_to_sarif(xml_report)
    print(json.dumps(sarif_xml, indent=2, ensure_ascii=False))

    return linter


if __name__ == "__main__":
    # Run main flow and get linter instance
    linter = main()

    # Simulate reporter_self for text reporter augmentation
    class DummyReporter:
        def __init__(self, report_folder, master):
            self.report_folder = report_folder
            self.master = master

    class DummyMaster:
        def __init__(self):
            self.report_folder = "tmp_test_roslynator"
            self.request_id = "test"
            self.config_file_name = "dummy"

    reporter = DummyReporter(report_folder="tmp_test_roslynator", master=DummyMaster())
    print("\nText reporter additional lines:")
    lines = linter.complete_text_reporter_report(reporter)
    for line in lines:
        print(line)

    sys.exit(0)
