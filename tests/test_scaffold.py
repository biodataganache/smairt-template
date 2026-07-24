import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cookiecutter.main import cookiecutter


TEMPLATE_ROOT = Path(__file__).resolve().parents[1]


class ScaffoldIntegrationTests(unittest.TestCase):
    def render_project(
        self, output_dir, project_mode, project_name, workflow_mode="ide_native"
    ):
        cookiecutter(
            str(TEMPLATE_ROOT),
            no_input=True,
            output_dir=str(output_dir),
            extra_context={
                "project_name": project_name,
                "project_mode": project_mode,
                "workflow_mode": workflow_mode,
                "create_git_repo": "no",
            },
        )
        return output_dir / project_name.lower().replace(" ", "_")

    def assert_rendered_sources(self, project):
        for pattern in ("*.py", "*.sh"):
            for path in project.rglob(pattern):
                content = path.read_text()
                self.assertNotIn("{{", content, path)
                self.assertNotIn("{%", content, path)

        slurm = project / "hpc" / "templates" / "slurm_basic.sh"
        subprocess.run(["bash", "-n", str(slurm)], check=True)

    def test_standard_project_renders_executable_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = self.render_project(
                Path(temp_dir), "standard", "Standard Render Test"
            )

            self.assert_rendered_sources(project)
            slurm_content = (
                project / "hpc" / "templates" / "slurm_basic.sh"
            ).read_text()
            self.assertIn("Paper-driven mode not enabled", slurm_content)

    def test_browser_paste_project_renders_executable_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = self.render_project(
                Path(temp_dir),
                "standard",
                "Browser Render Test",
                workflow_mode="browser_paste",
            )

            self.assert_rendered_sources(project)
            self.assertTrue((project / "prompts" / "session_log.md").exists())

    def test_generated_experiment_script_writes_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = self.render_project(
                Path(temp_dir), "standard", "Logger Render Test"
            )
            subprocess.run(
                [sys.executable, "scripts/new_script.py"],
                cwd=project,
                input="1\nsmoke_test\nLogging works\n1\n",
                text=True,
                check=True,
                capture_output=True,
            )

            script = project / "experiments" / "01_synthetic" / "script_01_smoke_test.py"
            subprocess.run(
                [sys.executable, str(script)],
                cwd=project,
                check=True,
                capture_output=True,
                text=True,
            )

            logs = list((project / "results" / "logs").glob("script_01_smoke_test_*.log"))
            self.assertEqual(len(logs), 1)
            self.assertIn("TODO: Implement experiment", logs[0].read_text())

    def test_paper_driven_lifecycle_generates_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = self.render_project(
                Path(temp_dir), "paper_driven", "Manifest Render Test"
            )
            self.assert_rendered_sources(project)
            self.assertIn(
                "SMAIRT Paper-Driven Mode",
                (project / "hpc" / "templates" / "slurm_basic.sh").read_text(),
            )
            self.assertIn(
                "Manifest Render Test",
                (project / "scripts" / "generate_manifest.py").read_text(),
            )

            subprocess.run(
                [
                    sys.executable,
                    "scripts/new_experiment.py",
                    "--section",
                    "01",
                    "--name",
                    "first_analysis",
                ],
                cwd=project,
                check=True,
                capture_output=True,
                text=True,
            )
            iteration = project / "analysis" / "01_first_analysis" / "iterations" / "iter_01"
            (iteration / "results" / "result.csv").write_text("value\n1\n")
            (iteration / "figures" / "figure.png").write_bytes(b"test figure")

            subprocess.run(
                [
                    sys.executable,
                    "scripts/finalize_iteration.py",
                    "--analysis",
                    "01_first_analysis",
                    "--iteration",
                    "01",
                ],
                cwd=project,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [sys.executable, "scripts/generate_manifest.py"],
                cwd=project,
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = (project / "FINAL_MANIFEST.md").read_text()
            self.assertIn("Manifest Render Test", manifest)
            self.assertIn("01_first_analysis", manifest)
            self.assertIn("iter_01", manifest)
            self.assertIn("| 01_first_analysis | iter_01 | 1 | 1 |", manifest)
            self.assertIn(
                "analysis/01_first_analysis/final/SELECTED.md", manifest
            )
            self.assertNotIn("| 01_first_analysis/iterations |", manifest)
            self.assertNotIn("| 01_first_analysis/final |", manifest)

    def test_template_has_no_obsolete_teelogger_calls(self):
        paths = [TEMPLATE_ROOT / "{{ cookiecutter.project_slug }}", TEMPLATE_ROOT / "demos"]
        for root in paths:
            for path in root.rglob("*.py"):
                self.assertNotIn("TeeLogger(log_dir=", path.read_text(), path)

    def test_manifest_supports_legacy_nested_analyses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = self.render_project(
                Path(temp_dir), "paper_driven", "Legacy Layout Test"
            )
            final_dir = project / "analysis" / "01_results" / "01_analysis" / "final"
            (final_dir / "results").mkdir(parents=True)
            (final_dir / "figures").mkdir()
            (final_dir / "SELECTED.md").write_text(
                "# Selected Iteration\n\n**Selected Iteration**: iter_03\n"
            )

            subprocess.run(
                [sys.executable, "scripts/generate_manifest.py"],
                cwd=project,
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = (project / "FINAL_MANIFEST.md").read_text()
            self.assertIn("| 01_results/01_analysis | iter_03 | 0 | 0 |", manifest)


if __name__ == "__main__":
    unittest.main()
