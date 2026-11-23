from principale.simulation import run_simulation


def test_simulation_reports_progress_without_external_actions():
    statuses = []
    values = iter([0.0, 0.9])
    result = run_simulation(
        ["fictive-1", "", "fictive-2"],
        error_rate=0.5,
        random_value=lambda: next(values),
        on_item=lambda index, url, status: statuses.append((index, url, status)),
    )

    assert result.total == 3
    assert result.traite == 1
    assert result.ignores == 1
    assert result.erreurs == 1
    assert len(statuses) == 3
    assert "simulé" in " ".join(status for _, _, status in statuses)
