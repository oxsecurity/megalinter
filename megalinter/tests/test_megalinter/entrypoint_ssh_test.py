import re
import unittest
from pathlib import Path

ENTRYPOINT = Path(__file__).resolve().parents[3] / "entrypoint.sh"


def non_root_sshd_options():
    content = ENTRYPOINT.read_text(encoding="utf-8")
    # The non-root branch starts sshd with its settings passed as -o options
    invocation = re.search(r"/usr/sbin/sshd -D \\\n(?:.*\\\n)*.*\n", content)
    return re.findall(r'-o "([A-Za-z]+) ', invocation.group(0))


class EntrypointSshTest(unittest.TestCase):
    # Alpine's openssh is built without PAM, so sshd warns on UsePAM (#9578)
    def test_non_root_sshd_does_not_pass_use_pam(self):
        self.assertNotIn("UsePAM", non_root_sshd_options())

    def test_non_root_sshd_keeps_password_authentication_disabled(self):
        self.assertIn("PasswordAuthentication", non_root_sshd_options())
