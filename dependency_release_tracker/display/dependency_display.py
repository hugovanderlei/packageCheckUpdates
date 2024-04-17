from rich.console import Console
from rich.markdown import Markdown
from datetime import datetime
import pytz


class DependencyDisplay:
    def __init__(self):
        self.console = Console()

    def display(self, dependencies, simple_output=False):
        """
        Display the dependencies information in the console using simple prints,
        with a full-width divider line between entries for both detailed and simple outputs.

        :param dependencies: A list of Dependency objects to display.
        :param simple_output: If True, display simplified output without release notes.
        """

        updated = "(UPDATED)"
        outdated = "(OUTDATED)"

        # Sorting the dependencies by published_at, handling None values appropriately
        # sorted_dependencies = sorted(
        #     dependencies,
        #     key=lambda x: (
        #         datetime.fromisoformat(x.published_at.rstrip("Z")).replace(
        #             tzinfo=pytz.utc
        #         )
        #         if x.published_at
        #         else datetime.min
        #     ),
        #     reverse=True,
        # )
        sorted_dependencies = sorted(
            dependencies,
            key=lambda x: self.ensure_datetime(x.published_at),
            reverse=True,
        )

        for dependency in sorted_dependencies:
            version_status = (
                updated
                if dependency.current_version == dependency.latest_version
                else outdated
            )
            version_status_color = "green" if version_status == updated else "red"
            # published_at = self.format_date(dependency.published_at)
            published_at_formatted = self.format_date(dependency.published_at)

            self.console.print(
                f"[yellow]{dependency.name} ({dependency.latest_version}) - "
                f"[white]{published_at_formatted} [{version_status_color}]{version_status}\n",
                style="bold",
            )

            if dependency.current_version != dependency.latest_version:
                self.console.print(
                    f"[red]Current version: {dependency.current_version}", style="bold"
                )

            if not simple_output:
                processed_notes = self.process_notes(dependency.notes)
                self.console.print(
                    Markdown(
                        f"Release notes:\n\n{processed_notes}\n\n[{dependency.url}]({dependency.url})"
                    )
                )
            self.console.print()
            self.console.rule(style="dim")
            self.console.print()

    @staticmethod
    def format_date(date_str):
        if not date_str:
            return "Date Unknown"
        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d %H:%M:%S")
        try:
            date_obj = datetime.fromisoformat(date_str.rstrip("Z") + "+00:00")
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return "Invalid Date"

    @staticmethod
    def process_notes(notes):
        """
        Process the release notes to add markdown formatting for better readability.
        Handle cases where versions might start directly with a '#' character.
        """

        if notes is None:
            return "No release notes available."

        processed_lines = []
        lines = notes.split("\n")
        for line in lines:
            if line.startswith("## ") or line.startswith("# "):
                # Extract the version number or header directly following '#'
                header_text = line.strip("#").strip()
                # Apply bold formatting only to version numbers and headers
                processed_lines.append(f"**{header_text}**")
            else:
                processed_lines.append(line)

        return "\n".join(processed_lines)

    def ensure_datetime(self, published_at):
        """
        Ensure that the published_at attribute is a datetime object.
        """
        if isinstance(published_at, str):
            # Convert string to datetime, assuming the string ends with 'Z' for UTC
            return datetime.fromisoformat(published_at.rstrip("Z") + "+00:00")
        elif isinstance(published_at, datetime):
            return published_at  # Return datetime if already converted
        return datetime.min  # Return a minimum datetime for None or invalid types
