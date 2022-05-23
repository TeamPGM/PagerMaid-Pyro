"""
pyromod - A monkeypatcher add-on for Pyrogram
Copyright (C) 2020 Cezar H. <https://github.com/usernein>

This file is part of pyromod.

pyromod is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyromod is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyromod.  If not, see <https://www.gnu.org/licenses/>.
"""
import math
from ..helpers import array_chunk

class Pagination:
    def __init__(self, objects, page_data=None, item_data=None, item_title=None):
        default_page_callback = (lambda x: str(x))
        default_item_callback = (lambda i, pg: f'[{pg}] {i}')
        self.objects = objects
        self.page_data = page_data or default_page_callback
        self.item_data = item_data or default_item_callback
        self.item_title = item_title or default_item_callback
    
    def create(self, page, lines=5, columns=1):
        quant_per_page = lines*columns
        page = 1 if page <= 0 else page
        offset = (page-1)*quant_per_page
        stop = offset+quant_per_page
        cutted = self.objects[offset:stop]
        
        total = len(self.objects)
        pages_range = [*range(1, math.ceil(total/quant_per_page)+1)] # each item is a page
        last_page = len(pages_range)
        
        
        nav = []
        if page <= 3:
            for n in [1,2,3]:
                if n not in pages_range:
                    continue
                text = f"· {n} ·" if n == page else n
                nav.append( (text, self.page_data(n)) )
            if last_page >= 4:
                nav.append(
                    ('4 ›' if last_page > 5 else 4, self.page_data(4))
                )
            if last_page > 4:
                nav.append(
                    (f'{last_page} »' if last_page > 5 else last_page, self.page_data(last_page))
                )
        elif page >= last_page-2:
            nav.extend([
                (f'« 1' if last_page-4 > 1 else 1, self.page_data(1)),
                (f'‹ {last_page-3}' if last_page-4 > 1 else last_page-3, self.page_data(last_page-3))
            ])
            for n in range(last_page-2, last_page+1):
                text = f"· {n} ·" if n == page else n
                nav.append( (text, self.page_data(n)) )
        else:
            nav = [
                (f'« 1', self.page_data(1)),
                (f'‹ {page-1}', self.page_data(page-1)),
                (f'· {page} ·', "noop"),
                (f'{page+1} ›', self.page_data(page+1)),
                (f'{last_page} »', self.page_data(last_page)),
            ]
        
        buttons = []
        for item in cutted:
            buttons.append(
                (self.item_title(item, page), self.item_data(item, page))
            )
        kb_lines = array_chunk(buttons, columns)
        if last_page > 1:
            kb_lines.append(nav)
        
        return kb_lines