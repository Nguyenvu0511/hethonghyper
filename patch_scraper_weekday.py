# -*- coding: utf-8 -*-
with open('src/scraper/mydtu_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'items.append({"raw_info": raw_info, "start_dt": dt.isoformat()})',
    'items.append({"raw_info": raw_info, "start_dt": dt.isoformat(), "weekday": wd_name})'
)

with open('src/scraper/mydtu_scraper.py', 'w', encoding='utf-8') as f:
    f.write(content)