from mc_options.cli import main


def test_cli_smoke_test(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "mc-options",
            "--paths",
            "1000",
            "--steps",
            "1",
            "--seed",
            "42",
        ],
    )

    main()

    captured = capsys.readouterr()
    assert "Monte Carlo result" in captured.out
    assert "black_scholes" in captured.out


def test_cli_implied_vol_smoke_test(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "mc-options",
            "implied-vol",
            "--target-price",
            "9.413403",
            "--spot",
            "100",
            "--strike",
            "100",
            "--rate",
            "0.03",
            "--maturity",
            "1",
        ],
    )

    main()

    captured = capsys.readouterr()
    assert "implied_volatility" in captured.out
