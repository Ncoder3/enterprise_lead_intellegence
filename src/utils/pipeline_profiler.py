import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class PipelineProfiler:
    """
    Lightweight profiler for measuring pipeline stages.
    """

    timings: dict[str, float] = field(default_factory=dict)

    @contextmanager
    def stage(self, name: str):
        """
        Measure the execution time of a pipeline stage.
        """

        start = time.perf_counter()

        try:
            yield

        finally:
            elapsed = time.perf_counter() - start

            self.timings[name] = (
                self.timings.get(name, 0.0) + elapsed
            )

    def total_time(self) -> float:
        """
        Return total measured stage time.
        """

        return sum(self.timings.values())

    def report(self) -> None:
        """
        Print a readable profiling report.
        """

        print()
        print("=" * 70)
        print("PIPELINE PERFORMANCE PROFILE")
        print("=" * 70)

        total = self.total_time()

        for stage, duration in self.timings.items():

            percentage = (
                (duration / total) * 100
                if total > 0
                else 0
            )

            print(
                f"{stage:<30} "
                f"{duration:>8.3f}s "
                f"({percentage:>6.2f}%)"
            )

        print("-" * 70)

        print(
            f"{'Measured Stage Time':<30} "
            f"{total:>8.3f}s"
        )

        print("=" * 70)