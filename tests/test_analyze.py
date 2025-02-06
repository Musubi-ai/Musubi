from ..musubi.utils import ConfigAnalyzer


def test_config_analyzer():
    analyzer = ConfigAnalyzer()
    res = analyzer.domain_analyze()
    print(res)

