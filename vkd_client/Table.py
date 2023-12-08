from dataclasses import dataclass
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import tabulate
from pydantic import Field


@dataclass
class Table:
    data: Dict[str, List[Any]]
    tablefmt: str = 'pretty'
    title: Optional[Union[str, int]] = None
    queries: Optional[List[str]] = None

    @property
    def formatted_title(self):
        if isinstance(self.title, int):
            return f"Table {self.title}."

        return self.title

    def __repr__(self):
        title = f"\n### {self.formatted_title}\n" if self.formatted_title is not None else ""
        if len(self.df) == 0:
            return f"{title}No entries."
        return f"{title}{tabulate.tabulate(self.df.values, headers=self.df.columns, tablefmt=self.tablefmt)}"

    def to_pandas(self):
        ret = pd.DataFrame(self.data)
        if self.queries is not None:
            for query in self.queries:
                ret = ret.query(query, engine='python')

        return ret

    @property
    def df(self):
        """Shortcut for to_pandas()"""
        return self.to_pandas()





