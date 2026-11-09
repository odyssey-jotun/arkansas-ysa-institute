# Arkansas YSA Institute (mock)

Mock site for the Institute of Religion class serving young adults in the Little Rock Arkansas Stake and the North Little Rock Arkansas Stake. Independent site, not owned or sponsored by The Church of Jesus Christ of Latter-day Saints.

Preview: https://odyssey-jotun.github.io/arkansas-ysa-institute/ (kept out of search with `noindex` and `robots.txt` until approved)

## Editing

`index.html`, `little-rock.html`, `events.html`, `faq.html` and `new-to-the-church.html` are generated. Edit `build.py`, then run:

```
python3 build.py
```

In `build.py`:

- `ADDRESS`, `CLASS_TIME`: where and when the Little Rock Stake class meets (Tuesdays at 7:00 PM in Benton). City only: the street address stays off the site.
- No house photo and no street address anywhere on the site, by Marc's request. The GroupMe is where people get the address.
- `EVENTS`, `BUILD_DATE`: upcoming events on `events.html` and the Little Rock page, each with its own `.ics` in `events/`. Past events drop off at build and in the browser.
- `GROUPME`: the class GroupMe join link.
- `STAKES`: each stake's tab, class card and units with Sunday times
- `FAQ_INSTITUTE`, `FAQ_CHURCH`: FAQ questions and answers (also written into FAQPage structured data)

Styles are in `styles.css`; fonts are self-hosted in `fonts/`.

## Sources

- Units, Sunday times and addresses: each unit's page on local.churchofjesuschrist.org, checked 2026-10-23. North Little Rock Stake unit list from the stake's own streaming site (nlrstake.org). Little Rock Stake towns from the Arkansas Democrat-Gazette, Aug. 8, 2025.
- Little Rock class time and place: from Marc, 2026-10-23.
- Elder Bednar devotional (Nov. 21, 2026): President Hartzell's text to Marc and Nikki, 2026-11-04. Zoom and GroupMe: Tony and Ashley Merrill, Oct. 2026.
- Registration steps and credit rules: Seminaries and Institutes help center, "How to Register for Institute."
- Ages 18 to 35: Church Newsroom, "Church Announces Age Adjustments for Young Adult Classifications," July 2024.
- Loneliness figure: Harvard Graduate School of Education, Making Caring Common, "Loneliness in America," 2021.
- FAQ topics: Ahrefs keyword volumes (US, monthly), noted beside each question in `build.py`.
- Photos: Unsplash (free license).
