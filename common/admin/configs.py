from typing import Dict


class ExportConfig:
    csv: bool = True
    excel: bool = True
    pdf: bool = True
    print: bool = True
    column_visibility: bool = True
    search_builder: bool = True

    def dict(self) -> Dict[str, bool]:
        return dict(
            csv=self.csv,
            excel=self.excel,
            pdf=self.pdf,
            print=self.print,
            column_visibility=self.column_visibility,
            search_builder=self.search_builder,
        )
