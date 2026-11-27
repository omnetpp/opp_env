import json
import os
import ssl
import subprocess
import urllib.error
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from opp_env import opp_env


real_get_telemetry_notice_marker_path = opp_env.get_telemetry_notice_marker_path

# keeps the tests from creating the notice marker in the real ~/.config
_marker_dir = tempfile.TemporaryDirectory()
_marker_patch = mock.patch.object(opp_env, "get_telemetry_notice_marker_path",
                                  return_value=os.path.join(_marker_dir.name, "omnetpp", "opp_env-telemetry-notice-shown"))

def setUpModule():
    _marker_patch.start()

def tearDownModule():
    _marker_patch.stop()
    _marker_dir.cleanup()


def project(name, version="1.0"):
    p = mock.Mock()
    p.name, p.version = name, version
    p.get_full_name.return_value = f"{name}-{version}"
    return p


class TelemetryEnabledTest(unittest.TestCase):
    def enabled(self, env):
        with mock.patch.dict(os.environ, env, clear=True):
            return opp_env.is_telemetry_enabled()

    def test_enabled_by_default(self):
        self.assertTrue(self.enabled({}))
        self.assertTrue(self.enabled({"OPP_ENV_NO_TELEMETRY": ""}))
        self.assertTrue(self.enabled({"DO_NOT_TRACK": ""}))

    def test_opt_out(self):
        self.assertFalse(self.enabled({"OPP_ENV_NO_TELEMETRY": "1"}))
        self.assertFalse(self.enabled({"DO_NOT_TRACK": "1"}))
        self.assertFalse(self.enabled({"DO_NOT_TRACK": "true"}))

    def test_any_non_empty_value_opts_out(self):
        for value in ("0", "false", "no"):
            self.assertFalse(self.enabled({"OPP_ENV_NO_TELEMETRY": value}))
            self.assertFalse(self.enabled({"DO_NOT_TRACK": value}))


class TelemetryUrlTest(unittest.TestCase):
    def url(self, env):
        code = "from opp_env import opp_env; print(opp_env.TELEMETRY_URL)"
        return subprocess.run([sys.executable, "-c", code], env={**env, "PATH": os.environ.get("PATH", "")},
                              cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
                              capture_output=True, text=True, check=True).stdout.strip()

    def test_default(self):
        self.assertEqual(self.url({}), "https://oppenv.omnetpp.org/report")

    def test_override(self):
        self.assertEqual(self.url({"OPP_ENV_TELEMETRY_URL": "http://localhost:8787/report"}), "http://localhost:8787/report")


class HostOsTest(unittest.TestCase):
    def detect(self, system, osrelease=None):
        if osrelease is None:
            opener = mock.Mock(side_effect=OSError)
        else:
            opener = mock.mock_open(read_data=osrelease)
        with mock.patch("platform.system", return_value=system), mock.patch("builtins.open", opener):
            return opp_env.detect_host_os()

    def test_macos(self):
        self.assertEqual(self.detect("Darwin"), "macos")

    def test_linux(self):
        self.assertEqual(self.detect("Linux", "6.8.0-45-generic\n"), "linux")

    def test_wsl2(self):
        self.assertEqual(self.detect("Linux", "5.15.153.1-microsoft-standard-WSL2\n"), "wsl")

    def test_wsl1(self):
        self.assertEqual(self.detect("Linux", "4.4.0-19041-Microsoft\n"), "wsl")

    def test_linux_without_proc(self):
        self.assertEqual(self.detect("Linux"), "linux")


class DownloadReportTest(unittest.TestCase):
    def report(self, env, dependency=False):
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(opp_env, "get_version", return_value="1.2.3"), \
                mock.patch.object(opp_env, "detect_host_os", return_value="macos"), \
                mock.patch("platform.machine", return_value="arm64"):
            return opp_env.get_download_report(project("omnetpp", "6.4.0aipre2"), dependency)

    def test_fields(self):
        self.assertEqual(self.report({}), {
            "project": "omnetpp", "version": "6.4.0aipre2", "dependency": False, "os": "macos",
            "arch": "arm64", "ci": False, "opp_env_version": "1.2.3"})

    def test_ci_and_dependency(self):
        self.assertFalse(self.report({"CI": "false"})["ci"])
        report = self.report({"CI": "true"}, dependency=True)
        self.assertTrue(report["ci"])
        self.assertTrue(report["dependency"])


class ReportDownloadTest(unittest.TestCase):
    def test_posts_json(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("urllib.request.urlopen") as urlopen:
            thread = opp_env.report_download(project("inet", "4.5.4"), dependency=True)
            thread.join()
        self.assertTrue(thread.daemon)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, opp_env.TELEMETRY_URL)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        body = json.loads(request.data)
        self.assertEqual((body["project"], body["version"], body["dependency"]), ("inet", "4.5.4", True))
        self.assertNotIn("url", body)
        self.assertEqual(urlopen.call_args.kwargs["timeout"], opp_env.TELEMETRY_TIMEOUT_SECONDS)

    def test_opted_out(self):
        with mock.patch.dict(os.environ, {"OPP_ENV_NO_TELEMETRY": "1"}, clear=True), \
                mock.patch("urllib.request.urlopen") as urlopen:
            self.assertIsNone(opp_env.report_download(project("inet")))
        urlopen.assert_not_called()

    def test_errors_are_swallowed(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("urllib.request.urlopen", side_effect=OSError("unreachable")):
            opp_env.report_download(project("inet")).join()


class CertificateFallbackTest(unittest.TestCase):
    def send(self, urlopen_error):
        report = {"project": "inet", "version": "4.5.4"}
        with mock.patch("urllib.request.urlopen", side_effect=urlopen_error), \
                mock.patch("subprocess.run") as run:
            opp_env.send_download_report(report)
        return run

    def test_certificate_error_falls_back_to_curl(self):
        run = self.send(urllib.error.URLError(ssl.SSLCertVerificationError("unable to get local issuer certificate")))
        args, kwargs = run.call_args
        self.assertEqual(args[0][0], "curl")
        self.assertEqual(args[0][-1], opp_env.TELEMETRY_URL)
        self.assertEqual(json.loads(kwargs["input"]), {"project": "inet", "version": "4.5.4"})

    def test_other_errors_do_not_fall_back(self):
        run = self.send(urllib.error.URLError(ConnectionRefusedError()))
        run.assert_not_called()

    def test_missing_curl_is_swallowed(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError(ssl.SSLCertVerificationError("x"))), \
                mock.patch("subprocess.run", side_effect=FileNotFoundError("curl")):
            opp_env.send_download_report({"project": "inet", "version": "4.5.4"})


class WaitForPendingReportsTest(unittest.TestCase):
    def test_waits_for_a_quick_report(self):
        sent = threading.Event()
        def slow_urlopen(*args, **kwargs):
            time.sleep(0.1)
            sent.set()
            return mock.MagicMock()
        with mock.patch.object(opp_env, "_pending_reports", []), mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("urllib.request.urlopen", side_effect=slow_urlopen):
            opp_env.report_download(project("inet"))
            opp_env.wait_for_pending_reports(2)
        self.assertTrue(sent.is_set())

    def test_gives_up_on_a_slow_server(self):
        release = threading.Event()
        with mock.patch.object(opp_env, "_pending_reports", []), mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("urllib.request.urlopen", side_effect=lambda *args, **kwargs: release.wait(5)):
            opp_env.report_download(project("inet"))
            opp_env.report_download(project("omnetpp"))
            start = time.monotonic()
            opp_env.wait_for_pending_reports(0.2)
            elapsed = time.monotonic() - start
            release.set()
        self.assertLess(elapsed, 0.5)


class TelemetryNoticeTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.marker = os.path.join(self.dir.name, "omnetpp", "opp_env-telemetry-notice-shown")
        for patch in (mock.patch.object(opp_env, "_telemetry_notice_shown", False),
                      mock.patch.object(opp_env, "get_telemetry_notice_marker_path", return_value=self.marker)):
            patch.start()
            self.addCleanup(patch.stop)

    def notices(self, count=1, env={}):
        with mock.patch.dict(os.environ, env, clear=True), mock.patch("urllib.request.urlopen"), \
                mock.patch.object(opp_env._logger, "info") as info:
            for _ in range(count):
                thread = opp_env.report_download(project("inet"))
                if thread:
                    thread.join()
        return [c for c in info.call_args_list if "privacy" in c.args[0]]

    def test_shown_once_and_remembered(self):
        self.assertEqual(len(self.notices(2)), 1)
        self.assertTrue(os.path.exists(self.marker))
        opp_env._telemetry_notice_shown = False
        self.assertEqual(self.notices(), [])

    def test_unwritable_config_dir_shows_it_once_per_process(self):
        with mock.patch("os.makedirs", side_effect=PermissionError("read-only")):
            self.assertEqual(len(self.notices(2)), 1)
        self.assertFalse(os.path.exists(self.marker))

    def test_not_shown_when_opted_out(self):
        self.assertEqual(self.notices(env={"OPP_ENV_NO_TELEMETRY": "1"}), [])
        self.assertFalse(os.path.exists(self.marker))

    def test_not_shown_in_ci(self):
        self.assertEqual(self.notices(env={"CI": "true"}), [])
        self.assertFalse(os.path.exists(self.marker))
        self.assertEqual(len(self.notices(env={"CI": "false"})), 1)

    def test_marker_path_follows_xdg_config_home(self):
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/cfg", "HOME": "/home/u"}):
            self.assertEqual(real_get_telemetry_notice_marker_path(), "/cfg/omnetpp/opp_env-telemetry-notice-shown")
        with mock.patch.dict(os.environ, {"HOME": "/home/u"}, clear=True):
            self.assertEqual(real_get_telemetry_notice_marker_path(), "/home/u/.config/omnetpp/opp_env-telemetry-notice-shown")


class NoticeBeforeDownloadTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        opp_env.Workspace.init_workspace(self.dir.name)
        self.workspace = opp_env.Workspace(self.dir.name)
        self.project = opp_env.resolve_projects(["omnetpp-6.1.0"])[0]

    def shown(self, env={}, local=False):
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(opp_env, "show_telemetry_notice_once") as notice:
            self.workspace.show_telemetry_notice_before_download([self.project], local)
        return notice.called

    def test_shown_before_a_download(self):
        self.assertTrue(self.shown())

    def test_not_shown_without_a_report_to_come(self):
        self.assertFalse(self.shown(local=True))
        self.assertFalse(self.shown({"OPP_ENV_NO_TELEMETRY": "1"}))
        os.makedirs(self.workspace.get_project_root_directory(self.project))
        self.assertFalse(self.shown())


class IsDependencyTest(unittest.TestCase):
    def test_is_dependency(self):
        specified = [project("simu5g")]
        self.assertFalse(opp_env.is_dependency(project("simu5g"), specified))
        self.assertTrue(opp_env.is_dependency(project("inet"), specified))


if __name__ == "__main__":
    unittest.main()
