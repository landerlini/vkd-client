from dataclasses import dataclass
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import tabulate


@dataclass
class Table:
    data: Dict[str, List[Any]]
    tablefmt: str = 'pretty'
    title: Optional[Union[str, int]] = None

    @property
    def formatted_title(self):
        if isinstance(self.title, int):
            return f"Table {self.title}."

        return self.title

    def __repr__(self):
        title = f"\n### {self.formatted_title}\n" if self.formatted_title is not None else ""
        return f"{title}{tabulate.tabulate(self.data, headers='keys', tablefmt=self.tablefmt)}"

    def to_pandas(self):
        return pd.DataFrame(self.data)

    @property
    def df(self):
        """Shortcut for to_pandas()"""
        return self.to_pandas()





