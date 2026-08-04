from hotglue_smoke_test.vcr.tap import VCRTapTestRunner

from tap_airwallex.tap import TapAirwallex


class Runner(VCRTapTestRunner):
    FILTER_HEADERS = [
        *VCRTapTestRunner.FILTER_HEADERS,
        "x-api-key",
        "x-client-id",
        "x-login-as",
    ]
    PRESERVE_KEYS = {"next_cursor", "expires_at", "has_more"}

    def module(self) -> str:
        return "tap_airwallex.tap"

    def launch(self):
        TapAirwallex.cli()


if __name__ == "__main__":
    Runner.main()